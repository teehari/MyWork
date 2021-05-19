    from PIL import Image
    import cv2
    import numpy as np
    import os
    import itertools as it
    import imutils
    import pytesseract
    import glob
    import pytesseract
    from pytesseract import Output
    import pandas as pd
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
    import shutil
    from skimage.measure import compare_ssim


    fuzzyThresh = 90
    ocrMatchThresh = 0.7
    ocrPageConsiderPercent = 0.3
    imgSimFlannMthcDist = 0.85
    imgSimFlannMthThresh = 0.25
    FLANN_INDEX_LSH = 6
    index_params = dict(algorithm=FLANN_INDEX_LSH,
                        table_number=4,  # 12
                        key_size=5,     # 20
                        multi_probe_level=2)  # 2
    flann = cv2.FlannBasedMatcher(index_params)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


    fileExtension = ['.tif', '.tiff']
    sampleFolder = r"D:\Sample-Invoice"
    sampleFolder = r"D:\Backup\Sample-Invoice\Alphabet"
    # outputBaseFolder = r"D:\InvoiceSeperated"
    outputBaseFolder = r"D:\Backup\Sample-Invoice\Alphabet\seperated"
    referenceFolder = r"D:\Backup\Sample-Invoice\Alphabet\seperated\VendorsReference"

    knownDescriptor = {}
    knownImage = {}
    knownOcr = {}
    invoiceProcessed = []
    orb = cv2.ORB_create()

    def readReferenceTemplates():

        if os.path.exists(referenceFolder):

            for files in os.listdir(referenceFolder): # Read reference Folder if any
                filename = os.path.basename(files).split(".")[0]
                try:
                    files = os.path.join(referenceFolder, files)
                    img = cv2.imread(files, 0)
                    img = cv2.medianBlur(img,3)
                    kp, desc = orb.detectAndCompute(img, None)
                    formatNo = filename.split("_")[1]
                    knownDescriptor[formatNo] = desc
                    knownImage[formatNo] = img
                    invoiceProcessed.append(formatNo)
                except Exception as e:
                    raise e

        else:
            os.mkdir(referenceFolder)

    def deskewImageNew(img):
        #Correct Skewness of image and return the image
        try:
            img1 = img.copy()
            osd = pytesseract.image_to_osd(img1[:img1.shape[0] // 2,:])
            rotationAngle = int(osd.split("\n")[2].split(":")[1].strip())
            img1 = imutils.rotate_bound(img1,rotationAngle)
            return img1
        except Exception as e:
            print("\tDeskewing Failed :-",e)
            return img

    def findImageSimilarity(pageDesc, referenceImgDec):
        try:
            matches = flann.knnMatch(pageDesc, referenceImgDec, k=2)

            matchCount = 0
            for i, match in enumerate(matches):
                if len(match) == 2:
                    if match[0].distance < imgSimFlannMthcDist * match[1].distance:
                        matchCount += 1
            if len(matches) > 0:
                topMatchPercent = matchCount / len(matches)
            else:
                topMatchPercent = 0

            matchPercent = topMatchPercent
            return matchPercent
        except Exception as e:
            print(e)
            return -1

    def CheckSimilarityWithMem(filepath):
        flannMatch = 0
        ssimMatch = 0
        ocrMatch = 0
        vendorMap = []
        similaritiesMap = []
        ssimSimilarityMap =[]
        ocrSimilarityMap = []
        vendorMappedFlann = None
        vendorMappedOCR = None
        vendorMappedSSIM = None
        newInvoiceFlag = False

        makeTiffCompressed(filepath)
        img = cv2.imread(filepath, 0)
        img = cv2.medianBlur(img,3)
        img = deskewImageNew(img)
        kp, desc = orb.detectAndCompute(img, None)
        for invoice in knownDescriptor:
            fsim = findImageSimilarity(desc, knownDescriptor[invoice])
            similaritiesMap.append(fsim)
            ssim = equivalent_dimension_sklearn(img,knownImage[invoice])
            ssimSimilarityMap.append(ssim)
            ocrScore = ocrCompare(img, knownImage[invoice])
            ocrSimilarityMap.append(ocrScore)
            vendorMap.append(invoice)


        if len(knownDescriptor) > 0:
            flannMatch = max(similaritiesMap)
            matchIndex = similaritiesMap.index(flannMatch)
            vendorMappedFlann = vendorMap[matchIndex]

            ssimMatch = max(ssimSimilarityMap)
            matchIndex = ssimSimilarityMap.index(ssimMatch)
            vendorMappedSSIM = vendorMap[matchIndex]

            ocrMatch = max(ocrSimilarityMap)
            matchIndex = ocrSimilarityMap.index(ocrMatch)
            vendorMappedOCR = vendorMap[matchIndex]

        else:
            print("I think it's First Invoice")
            newInvoiceFlag = True

        return newInvoiceFlag, img, flannMatch, vendorMappedFlann, ssimMatch, vendorMappedSSIM, ocrMatch, vendorMappedOCR

    def fzCmpLists(l1,refList, threshold):
        # print(type(l1))
        ll1 = len(l1)
        matchLen = 0
        for l in l1:
            word, ratio = process.extract(l,refList,
                                          scorer = fuzz.ratio,
                                          limit = 1)[0]
            if ratio >= threshold:
                matchLen += 1
        return matchLen/ll1

    def equivalent_dimension_sklearn(imageA,imageB):
        try:

            first_d =max(imageA.shape[0],imageB.shape[0])
            sec_d =min(imageA.shape[1],imageB.shape[1])
            thi_per= first_d*0.3

            y=0
            x=0
            crop_img = imageA[:round(thi_per),x:sec_d]
            crop_img2 = imageB[y:y+round(thi_per),x:sec_d]
            # cv2.imwrite(r"C:\Users\Admin\Pictures\test_case1.tiff",crop_img)
            # cv2.imwrite(r"C:\Users\Admin\Pictures\test_case2.tiff",crop_img2)

            (score, diff) = compare_ssim(crop_img, crop_img2, full=True)

            return score

        except Exception as e:
            print("Error in equivalent_dimension",e)

    def ocrCompare(img_1,img_2):

        ocr1 = pytesseract.image_to_data(img_1[:round(img_1.shape[0]*ocrPageConsiderPercent),:],
                                         output_type=Output.DICT,
                                         lang = "eng")
        ocr2 = pytesseract.image_to_data(img_2[:round(img_2.shape[0]*ocrPageConsiderPercent),:],
                                         output_type=Output.DICT,
                                         lang = "eng")

        df1 = pd.DataFrame(ocr1)
        df2 = pd.DataFrame(ocr2)
        df1 = df1[df1["text"] != ""]
        df2 = df2[df2["text"] != ""]
        l1 = list(df1["text"]) 
        l2 = list(df2["text"])
        return(fzCmpLists(l1,l2,fuzzyThresh))

    def makeTiffCompressed(filepath):
        try:
            # print("\tTiff Compression Started")
            img = Image.open(filepath)
            img.load()
            imlist =[]
            for page in range(0,img.n_frames):
                img.seek(page)
                imlist.append(img.convert("RGB"))
            imlist[0].save(filepath, compression="tiff_deflate", save_all=True,
                   append_images=imlist[1:])
            # print("\tTiff Compression Ended")
            return True
        except Exception as e:
            print("\tTiff Compression Failed",e)
            return False

    def copyFileToRequiredFolder(filepath):
        # vendorSimiartities = {}
        imageMatchSatified = False
        ocrMatchSatified = False
        ocrScore = 0
        tempList = []

        newInvoiceFlag, img, flannsimilarities, vendorMappedFlann, ssimMatch, vendorMappedSSIM, ocrMatch, vendorMappedOCR = CheckSimilarityWithMem(filepath)

        for value in flannsimilarities:
            if vale > imgSimFlannMthThresh :
                tempList.append(1)
            else:
                tempList.append(0)




        if flannSimilarity != 0 and flannSimilarity > imgSimFlannMthThresh:
            imageMatchSatified = True

        if ocrScore != 0 and ocrScore > ocrMatchThresh:
            ocrMatchSatified = True

        print("\tImage Similarity",imageMatchSatified,flannSimilarity,vendorMapped)
        print("\tOCR Similarity",ocrMatchSatified, ocrScore)

        if imageMatchSatified and ocrMatchSatified:
            print("\t\tFormat_"+ str(vendorMapped))
            filename = os.path.basename(filepath)
            formatNo = "Format_"+ str(vendorMapped)
            newFolderPath = os.path.join(outputBaseFolder, formatNo)
            newFilePath = os.path.join(newFolderPath,filename)
            shutil.copyfile(filepath,newFilePath)

        # elif imageMatchSatified and not ocrMatchSatified: # Create new folder and move it
        # 	print("\t\tUnknown")
        # 	filename = os.path.basename(filepath)
        # 	formatNo = "unknown"
        # 	newFolderPath = os.path.join(outputBaseFolder, formatNo)
        # 	newFilePath = os.path.join(newFolderPath,filename)
        # 	if not os.path.exists(newFolderPath):
        # 		os.mkdir(newFolderPath)
        # 	shutil.copyfile(filepath,newFilePath)

        else: # New Image Found
            print("\t\tNew Format_"+str(len(invoiceProcessed)+1))
            filename = os.path.basename(filepath)
            formatNo = "Format_"+str(len(invoiceProcessed)+1)
            newFolderPath = os.path.join(outputBaseFolder, formatNo)
            newFilePath = os.path.join(newFolderPath,filename)
            referenceFolderpath = os.path.join(outputBaseFolder,"VendorsReference")
            referenceFilepath = os.path.join(referenceFolderpath,formatNo+".tif")
            if not os.path.exists(referenceFolderpath):
                os.mkdir(referenceFolderpath)
            shutil.copyfile(filepath,referenceFilepath)
            kp, desc = orb.detectAndCompute(img, None)
            if not os.path.exists(newFolderPath):
                os.mkdir(newFolderPath)
            shutil.copyfile(filepath,newFilePath)
            knownDescriptor[str(len(invoiceProcessed)+1)] = desc
            knownImage[str(len(invoiceProcessed)+1)] = vendorImage
            # print(str(len(invoiceProcessed)+1))
            invoiceProcessed.append(str(len(invoiceProcessed)+1))


    readReferenceTemplates() # Read the Reference Template Folder - If Required

    for root, dirs, files in os.walk(sampleFolder, topdown=False):
        for name in files:
            if name.lower().endswith(tuple(fileExtension)):
                print(os.path.join(root, name))
                copyFileToRequiredFolder(os.path.join(root, name))

        for name in dirs:
            if name.lower().endswith(tuple(fileExtension)):
                print(os.path.join(root, name))
                copyFileToRequiredFolder(os.path.join(root, name))

