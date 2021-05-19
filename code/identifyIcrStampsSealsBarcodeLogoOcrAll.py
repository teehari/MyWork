# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:28:56 2020

@author: Hari
"""

import os
import cv2
import numpy as np
import traceback
from PIL import Image
from tesserocr import PyTessBaseAPI as tess, PSM, OEM, RIL
import pandas as pd
import time
#import pytesseract
import string
import re
from dateutil.parser import parse

#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR5.0alpha\tesseract.exe"

api = tess(path=r"C:\Program Files\Tesseract-OCR5.0alpha\tessdata")
api2 = tess(path=r"C:\Program Files\Tesseract-OCR5.0alpha\tessdata",
                                  psm=PSM.OSD_ONLY)

maxBorder = 50
punct = list(string.punctuation)

labellist = ['invoice','inv','quantity','qty','item','po','number',
             'no.','description','desc','payment','terms','net',
             'days','due','date','dt','reference','vat','tax',
             'total','unit','units','price','amount','amt','bill','ship',
             'billing','shipping','address','payment','reference',
             'value','unit','purchase','ref','uom','weight','wt',
             'services','service','fee','charge','charges','gst',
             'rate','currency','order','discount','subtotal','sub-total',
             'ship','balance','code','period','bank','remittance','account',
             'advice','customer']

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

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except:
        return False

def findZeroPattern(vals):
    binaryVals = vals // 255
    arr1 = np.concatenate(([0],binaryVals))
    arr2 = np.concatenate((binaryVals,[0]))
    ptnVals = np.bitwise_and(arr1,arr2)[1:]

    iszero = np.concatenate(([0], np.equal(ptnVals, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

def findLines(img,height,width):
    try:
        hLines = 0
        vLines = 0
        thresh = 200
        for i in range(width):
            single = img[:,i:i+1][:,0]
            if len(single) > 0:
                vLines1 = findZeroPattern(single)
                for line in vLines1:
                    if line[1] - line[0] >= thresh:
                        vLines += 1
        for i in range(height):
            single = img[i:i+1,:][0]
            if len(single) > 0:
                hLines1 = findZeroPattern(single)
                for line in hLines1:
                    if line[1] - line[0] >= thresh:
                        hLines += 1
        return hLines, vLines
    except Exception as e:
        print(traceback.print_exc(),e)
        return 0, 0

def findBlackWhiteDensity(img):
    try:
        img = img.astype(int)
        binaryVals = img // 255
        total = np.size(binaryVals)
        whites = np.sum(binaryVals)
        blacks = total - whites
        return blacks/total, whites/total
    except Exception as e:
        print(traceback.print_exc(),e)
        return 0,1

def findOverlaps(rect, boxes):
    try:
        overlappingBoxes = []
        overlappingIndexes = []
        for i,box in enumerate(boxes):
            if (len(box) == 4) and (len(rect) == 4):
                if isOverlap(rect,box):
                    overlappingBoxes.append(box)
                    overlappingIndexes.append(i)
        return overlappingBoxes, overlappingIndexes
    except Exception as e:
        print(e,"Find Overlaps")
        return None, None

def isOverlap(rect1, rect2):
    try:
        if (rect1[1] < rect2[1]) and (rect1[3] < rect2[1]):
            return False
        elif (rect1[0] < rect2[0]) and (rect1[2] < rect2[0]):
            return False
        elif (rect2[1] < rect1[1]) and (rect2[3] < rect1[1]):
            return False
        elif (rect2[0] < rect1[0]) and (rect2[2] < rect1[0]):
            return False
        else:
            return True
    except Exception as e:
        print(e,"isOverlap")
        return False

def detectRegions(img):
    try:
        mser = cv2.MSER_create()
        hierarchy, boxes = mser.detectRegions(img)
        return hierarchy, boxes
    except Exception as e:
        print(traceback.print_exc(),e)
        return None, None

def combineBoxes(boxes, height, width):

    try:
        loopOn = True
        rect = None
        combinedBoxes = []
        overlaps = False

        while loopOn:
            if (rect is None) and (len(boxes) > 0):
                rect = boxes[0]
            if rect is not None:
                overlapRects,overlapIndices = findOverlaps(rect,boxes)

                if len(overlapRects) > 0:
                    overlapRects.append(rect)
                    overlaps = True
                    newLeft = max(np.min([box[0] for box in overlapRects]),maxBorder)
                    newTop = max(np.min([box[1] for box in overlapRects]),maxBorder)
                    newRight = min(np.max([box[2] for box in overlapRects]),width - maxBorder)
                    newBottom = min(np.max([box[3] for box in overlapRects]),height - maxBorder)

                    for rect1 in overlapRects:
                        if rect1 in boxes:
                            i = boxes.index(rect1)
                            boxes.pop(i)

                    rect = [newLeft,newTop,newRight,newBottom]
                    if len(boxes) == 0:
                        combinedBoxes.append(rect)
                else:
                    combinedBoxes.append(rect)
                    if not overlaps:
                        boxes.pop(0)
                    overlaps = False
                    if len(boxes) > 0:
                        rect = boxes[0]

            loopOn = len(boxes) > 0
    except Exception as e:
        print(e)
        return []
    return combinedBoxes

inp = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\test"
out = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\outliers\test"

d = []

cnt = 0
filepaths = []
rerun = True

for root, subfolder, files in os.walk(inp):
    for fileName in files:
        outdir = root.replace(inp,out)
        os.makedirs(outdir, exist_ok = True)
        inppath = os.path.join(root,fileName)
        outpath = os.path.join(outdir,fileName)
        process = True
        if not rerun:
            if os.path.isfile(outpath + "_outliers.xlsx"):
                process = False

        if process:
            result,imgs = cv2.imreadmulti(inppath)
            imgarr = []
            prearr = []
            newimage = np.zeros((3000,3000))
            d = []

            for ind,img in enumerate(imgs):
                dim = img.shape
                if len(dim) == 3:
                    # Converting color image to grayscale image
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                height = img.shape[0]
                width = img.shape[1]
                heightTenPerc = height // 10
                widthTenPerc = width // 10
                blur = cv2.medianBlur(img,3)
                #Binarization of image - Make it strictly black or white 0 or 255
                pre = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                hierarcy,boxes = detectRegions(pre)
                boxCoords = [[int(box[0]),int(box[1]),int(box[0] + box[2]),
                              int(box[1] + box[3])] for box in boxes]
                heights = [(box[3] - box[1]) for box in boxCoords]
                widths = [(box[2] - box[0]) for box in boxCoords]
                mdnWd = np.median(widths)
                mdnHt = np.median(heights)
    
                expandedBoxes = [[box[0] - (3 * int(mdnWd)),
                                  box[1],
                                  box[2] + (3 * int(mdnWd)),
                                  box[3]] for i,box in enumerate(boxCoords)]

                expandedBoxes = [box for box in expandedBoxes if box[3] - box[1] >= mdnHt]
                boxes = combineBoxes(expandedBoxes,height,width)

                cpy1 = pre.copy()
                cpy = np.stack([cpy1,cpy1,cpy1],axis = 2)
                threshHt = min(3 * mdnHt, 100)
                
                #Run OCR for the entire image
                imgbinary = Image.fromarray(img)
                api.SetImage(imgbinary)
                ocrboxes = api.GetComponentImages(RIL.TEXTLINE,True)
                ocrText = {}
                for ocrboxNo, (im,ocrbox,_,_) in enumerate(ocrboxes):
                    rect2 = [ocrbox["x"],ocrbox["y"],
                             ocrbox["x"]+ocrbox["w"],
                             ocrbox["y"]+ocrbox["h"]]
                    for boxNo,box in enumerate(boxes):
                        rect1 = [box[0],box[1],box[2],box[3]]
                        overlap = isOverlap(rect1,rect2)
                        if overlap:
                            api.SetRectangle(ocrbox['x'],ocrbox['y'],
                                             ocrbox['w'],ocrbox['h'])
                            if boxNo in ocrText.keys():
                                ocrText[boxNo] = ocrText[boxNo] + api.GetUTF8Text()
                            else:
                                ocrText[boxNo] = api.GetUTF8Text()

                for boxno,box in enumerate(boxes):
                    if box[3] - box[1] >= threshHt:
                        sectHt = int((box[3] - box[1]) * 1.5)
                        sectWd = int((box[2] - box[0]) * 1.5)
                        imgsection = np.zeros((sectHt,sectWd))
                        imgsection = imgsection + 255
                        imgsection = imgsection.astype(int)
                        midPt = (sectHt / 2,
                                 sectWd / 2)
                        boxHf = ((box[3] - box[1]) / 2,
                                 (box[2] - box[0]) / 2)
                        sectTop = int(midPt[0]-boxHf[0])
                        sectDown = int(midPt[0]+boxHf[0])
                        sectLeft = int(midPt[1]-boxHf[1])
                        sectRight = int(midPt[1]+boxHf[1])
                        imgsection[sectTop:sectDown,sectLeft:sectRight] = pre[box[1]:box[3],box[0]:box[2]]
                        noHlines, noVlines = findLines(imgsection, sectHt, sectWd)
                        black,white = findBlackWhiteDensity(imgsection[sectTop:sectDown,
                                                                       sectLeft:sectRight])
                        ht = box[3] - box[1]
                        wd = box[2] - box[0]
                        hdiff = ht - mdnHt
                        wdiff = wd - mdnWd
                        noSingleChars = 0
                        noSingleDigit = 0
                        noSinglePunct = 0
                        noAmount = 0
                        noNumbers = 0
                        noDates = 0
                        noKeyWords = 0
                        noWords = 0
                        noPuncts = 0
                        noChars = 0
                        orientation, direction, order, deskew_angle = -1,-1,-1,-1

                        rgn = {}
                        rgn["filename"] = fileName
                        rgn["page"] = ind + 1
                        rgn["ht"] = ht
                        rgn["wd"] = wd
                        rgn["hdiff"] = hdiff
                        rgn["wdiff"] = wdiff
                        rgn["left"] = box[0]
                        rgn["top"] = box[1]
                        rgn["hlines"],rgn["vlines"],rgn["black"],rgn["white"] = noHlines,noVlines,black,white
                        rgn["Single_chars"],rgn["Single_digit"],rgn["Single_punct"] = noSingleChars,noSingleDigit,noSinglePunct
                        rgn["amount"],rgn["numbers"],rgn["dates"],rgn["keywords"] = noAmount,noNumbers,noDates,noKeyWords
                        rgn["puncts"] = noPuncts
                        rgn["words"] = noWords
                        rgn["chars"] = noChars
                        rgn["text"] = ""
                        rgn["deskew_angle"] = deskew_angle
                        rgn["direction"] = direction
                        rgn["orientation"] = orientation
                        rgn["order"] = order
                        tmppath = outpath + "_" + str(time.time()) + ".tiff"
                        cv2.imwrite(tmppath,imgsection)

                        if (imgsection.shape[0] > 0) and (imgsection.shape[1] > 0):
                            imgbinary = Image.open(tmppath)
                            api2.SetImage(imgbinary)
#                            api2.Recognize()

                            if boxno in ocrText.keys():
                                text = ocrText[boxno]
                            else:
                                text = ""
                            rgn["text"] = text
                            noChars = len(text)
                            it = api2.AnalyseLayout()
                            if it is not None:
                                orientation, direction, order, deskew_angle = it.Orientation()

                            if noChars > 0:

                                noPuncts = sum([1 if g in punct else 0 for g in text])
                                textNoPunct = "".join([" " if g in punct else g for g in text])
                                text = textNoPunct.strip()
                                texts = text.split(" ")
                                noWords = len(texts)

                                for txt in texts:
                                    txt = txt.lower().strip()
                                    if (len(txt) == 1):
                                        if txt.isalpha():
                                            noSingleChars += 1
                                        elif txt.isdigit():
                                            noSingleDigit += 1
                                            noNumbers += 1
                                        else:
                                            noSinglePunct += 1
                                    elif len(txt) > 1:
                                        if isAmount(txt):
                                            noAmount += 1
                                        elif is_date(txt):
                                            noDates += 1
                                        elif txt.isdigit():
                                            noNumbers += 1
                                        elif txt in labellist:
                                            noKeyWords += 1
                        rgn["hlines"],rgn["vlines"],rgn["black"],rgn["white"] = noHlines,noVlines,black,white
                        rgn["Single_chars"],rgn["Single_digit"],rgn["Single_punct"] = noSingleChars,noSingleDigit,noSinglePunct
                        rgn["amount"],rgn["numbers"],rgn["dates"],rgn["keywords"] = noAmount,noNumbers,noDates,noKeyWords
                        rgn["puncts"] = noPuncts
                        rgn["words"] = noWords
                        rgn["chars"] = noChars
                        rgn["deskew_angle"] = deskew_angle
                        rgn["direction"] = direction
                        rgn["orientation"] = orientation
                        rgn["order"] = order
                        d.append(rgn)
                        os.remove(tmppath)
            df = pd.DataFrame(d)
            df.to_excel(outpath + "_ocrall_outliers.xlsx", index = False)
            filepaths.append(outpath + "_ocrall_outliers.xlsx")

t = str(time.time())
dfAll = None
for filepath in filepaths:
    dffile = pd.read_excel(filepath)
    dffile["filepath"] = filepath
    if dfAll is None:
        dfAll = dffile
    else:
        dfAll = dfAll.append(dffile)

dfAll.to_excel("outliers_ocrall_" + t + ".xlsx",index = False)

