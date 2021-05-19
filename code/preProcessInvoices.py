# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:53:08 2020

@author: Hari
"""

import os
import traceback
import pytesseract
import imutils
import cv2
import numpy as np
#import shutil
from PIL import Image

#src path
src = r"D:\Invoice Data Extraction\Sample_Invoices\Invoices\OLAM"
#src = r"d:\test_d"
#tgt path
tgt = r"D:\Invoice Data Extraction\Sample_Invoices\Invoices\tgt_OLAM"
#tgt = r"d:\test_r"

#tesseract model path
tessPath = r"C:\Program Files\Tesseract-OCR5.0alpha\tesseract.exe"

from ghostscript import Ghostscript as GS
#Get GhostScript executable. The executable path should be added to system parameters.
#In windows it would be "PATH" environmental variable
ghostExecutable = r"D:\gs9.50\bin\gswin64c.exe"
ghostPause = 1
ghostDevice = "-sDEVICE=tiffscaled"
ghostDownScale = 1
ghostDownScaleFactor = 1
ghostQuit = 1
ghostCommandNoPause = "-dNOPAUSE"
ghostCommandDsf = "-dDownScaleFactor="
ghostCommandQuit = "quit"
ghostCommandOut = "-o"
ghostCommandForce = "-c"


#Use GhostScript to convert PDF to tiff image
def convertPDFToTiff(src,dst):
    try:
        args = []
        bDst = dst.encode('utf-8')
        bSrc = src.encode('utf-8')

        args.append(b'' + ghostExecutable.encode('utf-8'))
        args.append(b'' + ghostDevice.encode('utf-8'))
        if ghostPause == 1:
            noPause = b"" + ghostCommandNoPause.encode('utf-8')
            args.append(noPause)
        if ghostDownScale == 1:
            args.append(b"" + ghostCommandDsf.encode('utf-8') + str(ghostDownScaleFactor).encode('utf-8'))

        args.append(b'' + ghostCommandOut.encode('utf-8'))
        args.append(b'' + bDst)
        args.append(b'' + bSrc)

        if ghostQuit == 1:
            args.append(b'' + ghostCommandForce.encode('utf-8'))
            args.append(b'' + ghostCommandQuit.encode('utf-8'))

        print(*args)
        g = GS(*args)
        g.exit()
    except Exception as e:
        print(traceback.print_exc(),e)
        return False, args
    return True, args

def convertPDFToTiff1(src,dst):
    try:
        args = []
        bDst = dst
        bSrc = src

        args.append(ghostExecutable)
        args.append(ghostDevice)
        if ghostPause == 1:
            noPause = ghostCommandNoPause
            args.append(noPause)
        if ghostDownScale == 1:
            args.append(ghostCommandDsf + str(ghostDownScaleFactor))

        args.append(ghostCommandOut)
        args.append(bDst)
        args.append(bSrc)

        if ghostQuit == 1:
            args.append(ghostCommandForce)
            args.append(ghostCommandQuit)

        print(*args)
        g = GS(*args)
        g.exit()
    except Exception as e:
        print(traceback.print_exc(),e)
        return False
    return True

def detectAndChangeBackColor(binarizedImg):
    #After image binarization an image can have white background with black fonts
    #OR black background with white fonts. The second case is a noise and we need to convert
    #to white background with black fonts. This function does that
    try:
        u, indices = np.unique(binarizedImg, return_inverse = True)
        axis = 0
        a = u[np.argmax(np.apply_along_axis(np.bincount, axis,
                                            indices.reshape(binarizedImg.shape),None,
                                            np.max(indices) + 1), axis = axis)]
        bckCol = np.argmax(np.bincount(a))
        if bckCol == 0:
            return np.bitwise_not(binarizedImg)
        else:
            return binarizedImg
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

def imageEnhancementNew(pre):
    #Apply image enhancement at a page level and
    #return the image object to the calling function
    #If required, this image will be stored in blobstore and URI will be sent
    #Read the image as a binary file also
    try:
        #Apply MedianBlur to remove Watermarks or other noisy and data with light fonts
#        pre = cv2.medianBlur(pre,3)

        #Binarization of image - Make it strictly black or white 0 or 255
        pre = cv2.threshold(pre, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        #Detect if background color is white or black. If black, change it to White
        pre = detectAndChangeBackColor(pre)

        return pre
    except Exception as e:
        print(traceback.print_exc(),e)
        return None


def deskewImageNew(img):
    #Correct Skewness of image and return the image
    try:
        img1 = img.copy()
        #Get text orientation from Tesseract
        pytesseract.pytesseract.tesseract_cmd = tessPath
        osd = pytesseract.image_to_osd(img1[:img1.shape[0] // 2,:])
        rotationAngle = int(osd.split("\n")[2].split(":")[1].strip())
        img2 = imutils.rotate_bound(img1,rotationAngle)
        print(rotationAngle)
        return img2
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

#Detect regions in an image
def detectRegions(img):
    try:
        mser = cv2.MSER_create()
        regions, bboxes = mser.detectRegions(img)
        return regions, bboxes
    except Exception as e:
        print(traceback.print_exc(),e)
        return None, None

cropBorder = 50

def cropImageNew(img):
#This function crops an image to scale
    try:
        maxBorder = cropBorder
        #crop White borders on all sides
        #Remove outlier boxes
        #For this, first detect regions
        #For each region find the aspect ratios i.e. height/width ratio
        #Find mean and SD of these ratios
        #Normalize the ratios to mean = 0 and SD = 1
        #Delete regions where the ratio is greater than 2 SD or less than -2 SD

        regions, boxes = detectRegions(img)
        aspectRatios = [box[2]//box[3] for box in boxes]
        meanAspect = np.mean(aspectRatios)
        stdAspect = np.std(aspectRatios)
        normAspects = [((aspect - meanAspect)/stdAspect) for aspect in aspectRatios]
        outliers = [i for i, aspect in enumerate(normAspects) if (aspect < -2) or (aspect > 2)]
        boxCopy = boxes.copy()
        boxCopy = np.delete(boxes,outliers,axis = 0)

        if len(boxCopy) == 0:
            return None
        #Keep the maximum border as 50 pixels (maxBorder)
        minLeft = max(np.min([box[0] for box in boxCopy]),maxBorder)
        minTop = max(np.min([box[1] for box in boxCopy]),maxBorder)
        maxRight = min(np.max([box[0] + box[2] for box in boxCopy]),img.shape[1] - maxBorder)
        maxBottom = min(np.max([box[1] + box[3] for box in boxCopy]),img.shape[0] - maxBorder)

        #Crop the image
        cpy = img.copy()        
        cpy = cpy[minTop:maxBottom,minLeft:maxRight]
        img_border = cv2.copyMakeBorder(
            cpy,
            top=maxBorder,
            bottom=maxBorder,
            left=maxBorder,
            right=maxBorder,
            borderType=cv2.BORDER_CONSTANT,
            value=[255,255,255]
        )

        #Write the cropped image to a file
        return img_border
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

import time
for root, sub, files in os.walk(src):
    if len(files) > 0:
        for filename in files:
            tgtFolder = root.replace(src,tgt)
            os.makedirs(tgtFolder,exist_ok = True)
            tgtPath = os.path.join(tgtFolder,filename)
            srcPath = os.path.join(root,filename)
            #Convert all pdf to tiff before hand
            if ".TIF" in os.path.splitext(filename)[1].upper():
                pages = cv2.imreadmulti(srcPath)[1]
                new_pages = []
                for i,page in enumerate(pages):
                    t = time.time()
                    enhanced = imageEnhancementNew(page)
                    print("enhanced",time.time() - t)
                    if enhanced is None:
                        enhanced = page
                    t = time.time()
                    deskewed = deskewImageNew(enhanced)
#                    print("deskewed",time.time() - t)
#                    pagePath = tgtPath + "_" + str(i) + "_deskew.tiff"
#
#                    if deskewed is not None:
#                        cv2.imwrite(pagePath,deskewed)
#                        print(tgtPath + "_" + str(i) + "_deskew.tiff")

                    if deskewed is None:
                        deskewed = enhanced
                    t = time.time()
                    cropped = cropImageNew(deskewed)
                    print("cropped", time.time() - t)
                    if cropped is None:
                        cropped = deskewed

                    cropArray = Image.fromarray(cropped)
                    new_pages.append(cropArray)
#                    pagePath = tgtPath + "_" + str(i) + ".tiff"
#                    cropArray.save(pagePath)
#                    cv2.imwrite(pagePath,deskewed)
#                    print(tgtPath + "_" + str(i) + ".tiff")

                new_pages[0].save(tgtPath,compression="tiff_adobe_deflate",
                      save_all=True,append_images=new_pages[1:])
                print(tgtPath)


