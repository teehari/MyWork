# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:35:20 2020

@author: Hari
"""
import time
import pandas as pd
import os
import sys
import re
import string
from tesserocr import PyTessBaseAPI as tess, PSM, OEM, RIL
from PIL import Image
import time
import cv2
import imutils
import multiprocessing as mp
from contextlib import contextmanager
from functools import partial
import traceback
import numpy as np
import pytesseract
import warnings
warnings.filterwarnings("ignore")

api = tess(r"C:\Program Files\Tesseract-OCR\tessdata",
           psm=PSM.AUTO_OSD,oem=OEM.LSTM_ONLY)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
punct = list(string.punctuation)

cropBorder = 50

#labellist = list(pd.read_csv("labels.csv")["word"])
keywordlist = ['invoice','inv','quantity','qty','item','po','number',
             'no.','description','desc','payment','terms','net',
             'days','due','date','dt','reference','vat','tax',
             'total','unit','units','price','amount','amt','bill','ship',
             'billing','shipping','address','payment','reference',
             'value','unit','purchase','ref','uom','weight','wt',
             'services','service','fee','charge','charges','gst',
             'rate','currency','order','discount','subtotal','sub-total',
             'ship','balance','code','period','bank','remittance','account',
             'advice']
punct = list(string.punctuation)

def isAmount(s):
    try:
        ptn1 = "[0-9]{1,3}[,]{1}[0-9]{3}[,]{1}[0-9]{3}[,]{1}[0-9]{3}[.]{1}[0-9]{1,4}"
        ptn2 = "[0-9]{1,3}[,]{1}[0-9]{3}[,]{1}[0-9]{3}[.]{1}[0-9]{1,4}"
        ptn3 = "[0-9]{1,3}[,]{1}[0-9]{3}[.]{1}[0-9]{1,4}"
        ptn4 = "[0-9]{1,3}[.]{1}[0-9]{1,4}"

        ptn5 = "[0-9]{1,3}[.]{1}[0-9]{3}[.]{1}[0-9]{3}[.]{1}[0-9]{3}[,]{1}[0-9]{1,4}"
        ptn6 = "[0-9]{1,3}[.]{1}[0-9]{3}[.]{1}[0-9]{3}[,]{1}[0-9]{1,4}"
        ptn7 = "[0-9]{1,3}[.]{1}[0-9]{3}[,]{1}[0-9]{1,4}"
        ptn8 = "[0-9]{1,3}[,]{1}[0-9]{1,4}"

        ptns = [ptn1,ptn2,ptn3,ptn4,ptn5,ptn6,ptn7,ptn8]

        for ptn in ptns:
            l = re.findall(ptn,s)
            l1 = [g for g in l if len(g) > 0]
            if len(l1) == 1:
                return True
    except:
        return False
    return False

def isDate(s, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    ptn2 = r"[0-9]{1,4}[\.\-\/]{1}[0-9]{1,4}[\.\-\/]{0,1}[0-9]{0,4}"
    ptn1 = r"[0-9]{1,4}[\.\-\/]{1}(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december){1}[\.\-\/]{0,1}[0-9]{0,4}"
    ptns = [ptn1,ptn2]

    try:
        for ptn in ptns:
            l = re.findall(ptn,s)
            l1 = [g for g in l if len(g) > 0]
            if len(l1) >= 1:
                return True
    except:
        return False

def getBoxesText(img, api, height, width):
    
    #Initialize an empty output
    ocrboxes = []
    
    #Get all the bounding boxes of the text Tesseract identified
    boxes = api.GetComponentImages(RIL.TEXTLINE, True)
    
    #Iterate through bounding boxes and get the text. Add to the results
    for i, (im, box, _, _) in enumerate(boxes):
        api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
        ocrResult = api.GetUTF8Text()
        ocrbox = {}
        ocrbox["x1"] = box["x"]
        ocrbox["y1"] = box["y"]
        ocrbox["x2"] = box["x"] + box["w"]
        ocrbox["y2"] = box["y"] + box["h"]
        ocrbox["w"] = box["w"]
        ocrbox["h"] = box["h"]
        ocrbox["rel_x1"] = round(box["x"] / width, 4)
        ocrbox["rel_y1"] = round(box["y"] / height, 4)
        ocrbox["rel_x2"] = round((box["x"] + box["w"]) / width, 4)
        ocrbox["rel_y2"] = round((box["y"] + box["h"]) / height, 4)
        ocrbox["rel_w"] = round(box["w"] / width, 4)
        ocrbox["rel_h"] = round(box["h"] / height, 4)
        ocrbox["text"] = ocrResult
        ocrboxes.append(ocrbox)
    
    return ocrboxes

def sort2keys(inp):
    return inp[0],inp[1]

def splitRectToRegions(boxes, hsection, vsection):
    
    #Create pairs of max X,Y coords for each section
    hvPairs = []
    for i in range(hsection):
        for j in range(vsection):
            x = (i + 1) * (1 / hsection)
            y = (j + 1) * (1 / vsection)
            hvPairs.append((x,y))
    hvPairs.sort(key=sort2keys)
    
    #Initialize Results
    splitRegions = {}
    for i in range(len(hvPairs)):
        splitRegions[i + 1] = []
    
    #Iterate through ocr boxes and arrange them in different quadrants
    for box in boxes:
        x = box["rel_x1"]
        y = box["rel_y1"]
        for quadrant,hv in enumerate(hvPairs):
            if (x <= hv[0]) and (y <= hv[1]):
                splitRegions[quadrant + 1].append(box)
                break
    return splitRegions

def findKeyAmtDate(boxes):
    
    #Define local variables for keywords, amounts, dates
    keywords = 0
    dates = 0
    amounts = 0
    result = {}
    keys = set([])

    for box in boxes:
        text = box["text"]
        text = text.lower().strip()
        if isAmount(text):
            amounts += 1
        elif isDate(text):
            dates += 1
        else:
            textNoPunct = "".join([" " if g in punct else g for g in text])
            texts = textNoPunct.split(" ")
            for smallText in texts:
                if smallText in keywordlist:
                    keys.add(smallText)
    keywords = len(keys)
    result["amounts"] = amounts
    result["dates"] = dates
    result["keywords"] = keywords
    return result

def initOcr(imgpath):
    
    #Open the image using Pillow and get it's height and width
    img = Image.open(imgpath,mode="r")
    
    #Give the image as an input to the tesseract API
    api.SetImage(img)
    
    return api, img

def initOcrNew(imgpath):

    #Give the image as an input to the tesseract API
    api.SetImageFile(imgpath)
    
    return api

def invPageOrNot(img, api):
    
    #Initialize Result
    invPage = True
    
    #Find image dimensions
    height = img.height
    width = img.width
        
    #Get ocrtext and it's bounding boxes
    ocrboxes = getBoxesText(img, api, height, width)
    
    #Split the page into two vertical halves
    #and find which boxes falls on left and which falls on right
    splitboxes = splitRectToRegions(ocrboxes,1,2)
    
    #Define variables
    #Keyword present or not in the entire page
    keywordAll = 0
    #Keyword present in the right page or not
    keywordRight = 0
    #Date present in the entire page
    dateAll = 0
    #Date present in the right half of the page
    dateRight = 0
    #Amount field present in the entire page
    amountAll = 0
    #Amount field present in the right half of the page
    amountRight = 0
    
    #Find keywords, amounts, date in left half and add to the count for entire page
    leftBoxes = splitboxes[1]
    leftResult = findKeyAmtDate(leftBoxes)
    
    #Find keywords, amounts, date in left half and add to the count for entire page
    rightBoxes = splitboxes[2]
    rightResult = findKeyAmtDate(rightBoxes)
    
    #Assign values to the variables
    keywordRight = rightResult["keywords"]
    keywordAll = leftResult["keywords"] + keywordRight
    amountRight = rightResult["amounts"]
    amountAll = leftResult["amounts"] + amountRight
    dateRight = rightResult["dates"]
    dateAll = leftResult["dates"] + dateRight

    #Check if a page is invoice page or not
    condition1 = (amountAll > 3)
    condition2 = (keywordAll >= 5) and (dateAll > 0)
    condition3 = (keywordRight > 0) and (amountRight > 0)
    invPage = condition1 or condition2 or condition3
    return invPage

def deskewAngle(osdapi,img):
    try:
        it = osdapi.AnalyseLayout()
        orientation, direction, order, deskew_angle = it.Orientation()
        if deskew_angle < 0:
            deskew_angle = 90 + deskew_angle
        angle = (orientation * 90) + deskew_angle
        deskew = 360 - angle
        return deskew
    except:
        # print("Deskew Error:",e)
        return -10000

def deskewImageNew(img):
    #Correct Skewness of image and return the image
    cpy = img.copy()
    try:
        #Get text orientation from Tesseract
        osd = pytesseract.image_to_osd(img)
        rotationAngle = int(osd.split("\n")[2].split(":")[1].strip())
        img1 = imutils.rotate_bound(img,rotationAngle)
        return img1
    except:
        return cpy


def deskewImage(osdapi,img):
    cpy = img.copy()
    try:
        it = osdapi.AnalyseLayout()
        orientation, direction, order, deskew_angle = it.Orientation()
        if deskew_angle < 0:
            deskew_angle = 90 + deskew_angle
        angle = (orientation * 90) + deskew_angle
        deskew = 360 - angle
        img = imutils.rotate_bound(img,round(deskew,0))
        return img
    except:
        # print("Deskew Error:",e)
        return cpy

@contextmanager
def poolcontext(*args, **kwargs):
    pool = mp.Pool(*args, **kwargs)
    pool.close()
    pool.join()
    pool.terminate()
    yield pool

def detectAndChangeBackColor(binarizedImg):
    #After image binarization an image can have white background with black fonts
    #OR black background with white fonts. The second case is a noise and we need to convert
    #to white background with black fonts. This function does that
    cpy = binarizedImg.copy()
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
        # print(traceback.print_exc(),e)
        return cpy

def imageEnhancementNew(pre):
    #Apply image enhancement at a page level and
    #return the image object to the calling function
    #If required, this image will be stored in blobstore and URI will be sent
    #Read the image as a binary file also
    cpy = pre.copy()
    try:
        #Apply MedianBlur to remove Watermarks or other noisy and data with light fonts
#        pre = cv2.medianBlur(pre,5)
        #Binarization of image - Make it strictly black or white 0 or 255
        pre = cv2.threshold(pre, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        #Detect if background color is white or black. If black, change it to White
        pre = detectAndChangeBackColor(pre)
        return pre
    except Exception as e:
        # print(traceback.print_exc(),e)
        return cpy

def detectRegions(img):
    try:
        mser = cv2.MSER_create()
        hierarchy, boxes = mser.detectRegions(img)
        return hierarchy, boxes
    except Exception as e:
        # print(traceback.print_exc(),e)
        return None, None

def cropImageNew(img):
    cpy = img.copy()
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
                cpy,top=maxBorder,bottom=maxBorder,left=maxBorder,
                right=maxBorder,borderType=cv2.BORDER_CONSTANT,
                value=[255,255,255]
                )
        #Write the cropped image to a file
        return img_border
    except Exception as e:
        # print(traceback.print_exc(),e)
        return cpy

def findInvPage(imgpath, tmpdir):

    dest_inv_pages = imgpath.replace("DATASET", "DATASET_INVOICE_PAGES_XXXX")
    dest_noninv_pages = imgpath.replace("DATASET", "DATASET_NONINVOICE_PAGES_XXXX")

    if(os.path.isfile(dest_noninv_pages) or os.path.isfile(dest_inv_pages)):
        print("Already processed: ", imgpath)
        return {}

    print("Processing: ", imgpath)
    #Temp file name based on timestamp
    temp = str(time.time()).split(".")[0]
    fnameWExtn = os.path.split(imgpath)[1]
    fname = os.path.splitext(fnameWExtn)[0]
    #Read multi pages
    ret, imgs = cv2.imreadmulti(imgpath)
    if len(imgs) == 1:
        imgs = [cv2.imread(imgpath,0)]
    #Initialize Result
    #Initialize all pages are invoice page
    pages = [1] * len(imgs)
    pageImgs = [None] * len(imgs)
    invPages = []
    nonInvPages = []
    tempfiles = []
    #Check each page is inv page or not
    for pageNo,img in enumerate(imgs):
        tempfilepath = os.path.join(tmpdir,fname + "_" + temp + "_" + str(pageNo + 1) + ".tiff")
        fileWritten = cv2.imwrite(tempfilepath,img)
        if fileWritten:
            #Initialize OCR
            api = initOcrNew(tempfilepath)
            #Perform Image Enhancement
            img = imageEnhancementNew(img)
            #Find Deskew angle and deskew the image
            img = deskewImage(api,img)
            #Crop the Image
            img = cropImageNew(img)
            #Write the deskewed,cropped image to disk and read again
            #Converting a cv2 array to pillow image using fromArray doesn't give good accuracy
            cv2.imwrite(tempfilepath,img)
            image = Image.open(tempfilepath)
            pageImgs[pageNo] = image
            #Find if the page is invoice page or not
            invPage = invPageOrNot(image, api)
            #Add to a list whether a page is invoice or not
            pages[pageNo] = int(invPage)
            #Deallocate OCR api
            api.Clear()
        tempfiles.append(tempfilepath)
    #If 1st and 3rd pages are invoice, but the 2nd is not. Add the 2nds page too as invoice page
    lastInvPage = -1
    try:
        lastInvPage = pages[::-1].index(1)
        lastInvPage = len(pages) - lastInvPage
    except:
        pass
    firstInvPage = -1
    try:
        firstInvPage = pages.index(1)
    except:
        pass
    for pageNo in range(len(imgs)):
        if (pageNo >= firstInvPage) and (pageNo < lastInvPage):
            invPages.append(pageImgs[pageNo])
        else:
            nonInvPages.append(pageImgs[pageNo])

    # Write file back and delete temporary files
    dest_folder = dest_inv_pages[: dest_inv_pages.rfind('/')+1]
    os.makedirs(os.path.dirname(dest_folder), exist_ok=True)

    dest_folder = dest_noninv_pages[: dest_noninv_pages.rfind('/')+1]
    os.makedirs(os.path.dirname(dest_folder), exist_ok=True)

    #If none of the pages are invoice pages, make everything invoice pages
    if len(invPages) == 0:
        invPages = nonInvPages.copy()
        nonInvPages = []

    if len(invPages) > 1:
        invPages[0].save(dest_inv_pages, save_all = True,append_images = invPages[1:])
    elif len(invPages) == 1:
        invPages[0].save(dest_inv_pages)

    if len(nonInvPages) > 1:
        nonInvPages[0].save(dest_noninv_pages, save_all = True,append_images = nonInvPages[1:])
    elif len(nonInvPages) == 1:
        nonInvPages[0].save(dest_noninv_pages)

    for tmpfile in tempfiles:
        if os.path.isfile(tmpfile):
            os.remove(tmpfile)

    dict_temp = {"File_Path": imgpath,
                "Invoice_Pages": len(invPages),
                "Non-Invoice_Pages": len(nonInvPages)}

    print("Processing Completed: ", imgpath)

    return dict_temp


def get_TIF_files(in_path):
    """
    Get all folders and file inside them in the path
    :param in_path:
    :return:
    """
    list_direct = [x[0] for x in os.walk(in_path)]
    list_files = [x[2] for x in os.walk(in_path)]
    assert len(list_direct) == len(list_files), "Error in reading files and folder structure in the path"

    list_dir_ = []
    list_files_ = []
    for index, dir_ in enumerate(list_direct):
        tif_files = []
        files = list_files[index]
        if ".DS_Store" in files:
            files.remove(".DS_Store")
        for f in files:
            if ".TIF" in f.upper():
                tif_files.append(f)
        if len(tif_files) > 0:
            list_dir_.append(dir_)
            list_files_.append(tif_files)

    return list_dir_, list_files_

def main():
    """
    Script needs invoice folder path to iterate over
    :return:
    """
    args = sys.argv
    if len(args) < 2:
        print("Input folder path is needed")
        print("Terminating Script")
        return

    in_path = args[1]

    list_dir, list_files = get_TIF_files(in_path)

    path_files = []
    for i in range(0, len(list_dir)):
        dir_ = list_dir[i]
        files = list_files[i]
        for f in files:
            path_files.append(os.path.join(dir_, f))


    pool_list = []
    for f in path_files:
        pool_list.append((f, "./"))

    pool = mp.Pool(mp.cpu_count())
    res_pool = pool.starmap(findInvPage, pool_list)
    pool.close()
    pool.join()
    dict_df = res_pool

    temp = str(time.time()).split(".")[0]
    pd.DataFrame(dict_df).to_csv("DF_PREPROCESSING_" + temp + ".csv")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Processing Time: ", (time.time() - start_time))



