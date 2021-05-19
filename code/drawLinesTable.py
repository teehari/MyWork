# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:28:56 2020

@author: Hari
"""
import os
import glob
import cv2
import numpy as np
import traceback
from PIL import Image
import pandas as pd
import time
import string
import re
import operator
import json

minColsForLnItmTbl = 2
maxBorder = 50

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

def isHCollinear(rect1, rect2):
    try:
        if (rect1[1] < rect2[1]) and (rect1[3] > rect2[1]):
            return True
        elif (rect2[1] < rect1[1]) and (rect2[3] > rect1[1]):
            return True
        else:
            return False
    except Exception as e:
        print(e,"isHCollinear")
        return False

def detectRegions(img):
    try:
        mser = cv2.MSER_create()
        hierarchy, boxes = mser.detectRegions(img)
        return hierarchy, boxes
    except Exception as e:
        print(traceback.print_exc(),e)
        return None, None

def combineBoxesNew(boxes, height, width, mdn):

    try:
        loopOn = True
        rect = None
        combinedBoxes = []
        overlaps = False
        smallerRegions = []
        constituents = []

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
                    if newRight <= newLeft:
                        newRight = newLeft + 1
                    if newBottom <= newTop:
                        newBottom = newTop + 1

                    for rect1 in overlapRects:
                        if rect1 in boxes:
                            i = boxes.index(rect1)
                            boxes.pop(i)

                    orgrect = [rect[0] + (3 * int(mdn["width"])),rect[1],
                               rect[2] - (3 * int(mdn["width"])),rect[3]]
                    smallerRegions.append(orgrect)

                    rect = [newLeft,newTop,newRight,newBottom]
                    if len(boxes) == 0:
                        combinedBoxes.append(rect)
                else:
                    if len(smallerRegions) == 0:
                        orgrect = [rect[0] + (3 * int(mdn["width"])),rect[1],
                                   rect[2] - (3 * int(mdn["width"])),rect[3]]
                        constituents.append([orgrect])
                    else:
                        constituents.append(smallerRegions)

                    smallerRegions = []
                    combinedBoxes.append(rect)
                    if not overlaps:
                        boxes.pop(0)
                    overlaps = False
                    if len(boxes) > 0:
                        rect = boxes[0]

            loopOn = len(boxes) > 0
            if not loopOn:
                if len(combinedBoxes) > len(constituents):
                    if len(smallerRegions) == 0:
                        orgrect = [rect[0] + (3 * int(mdn["width"])),rect[1],
                                   rect[2] - (3 * int(mdn["width"])),rect[3]]
                        constituents.append([orgrect])
                    else:
                        constituents.append(smallerRegions)
    except Exception as e:
        print(e)
        return [],[]
    return combinedBoxes,constituents

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
            if len(l1) >= 1:
                return True
    except:
        return False
    return False

inpfolder = r"D:\azuretemp\Header1"
outfolder = r"D:\azuretemp\Header1\out"
os.makedirs(inpfolder,exist_ok=True)
os.makedirs(outfolder,exist_ok=True)

inpfiles = glob.glob(os.path.join(inpfolder,"*.ocr.json") )

for inpfile in inpfiles:

    inp = inpfile.rstrip(".ocr.json")
    obj = json.loads(inpfile)
    lines = obj["analyzeResult"]["readResults"]["0"]["lines"]
    height = obj["analyzeResult"]["readResults"]["0"]["height"]
    width = obj["analyzeResult"]["readResults"]["0"]["width"]
    texts = []
    lefts = []
    tops = []
    rights = []
    bottoms = []
    rows = []
    boxes = []
    for line in lines:
        row = {}
        text = line["text"]
        row["text"] = text
        box = line["boundingBox"]
        left = min(box[0],box[6])
        row["left"] = left
        top = min(box[1],box[3])
        row["top"] = top
        right = max(box[2],box[4])
        row["right"] = right
        bottom = max(box[5],box[7])
        row["bottom"] = bottom
        rows.append(row)
        boxes.append([left,top,right,bottom,text])

    df = pd.DataFrame(rows)
    df["isTableLine"] = 0
    df["noNeighbours"] = 0
    df["isLastAmt"] = 0

    sboxes = sorted(boxes,key = operator.itemgetter(1))
    filename = inpfile.rstrip(".TIF.ocr.json")
    actualfilename = "_".join(filename.split("_")[0:-1])
    pageno = filename.split("_")[-1]
    result,imgs = cv2.imreadmulti(inp)
    img = imgs[pageno]
    cpy1 = img.copy()
    cpy = np.stack([cpy1,cpy1,cpy1],axis = 2)

    while len(sboxes) > 0:
        ref = sboxes[0]
        colluntil = 0
        for i in range(1,11):
            if len(sboxes) > i + 1:
                box = sboxes[i]
                isColl = isHCollinear(ref,box)
                if isColl:
                    colluntil += 1
                else:
                    break
        if colluntil >= minColsForLnItmTbl:
            mintop = min([box[1] for box in sboxes[:colluntil]])
            cv2.line(cpy,(0,mintop),(height,mintop),(0,255,0),thickness=2)

        del sboxes[:colluntil + 1]

    for boxId,box in enumerate(boxes):
        cv2.rectangle(cpy,(box[0],box[1]),
                      (box[2],box[3]),
                      (255,255,0),3)

    outpath = os.path.join(outfolder, os.path.split(inp)[1] + "_" + str(pageno) + ".TIF")
    cv2.imwrite(outpath,cpy)
    

#    result,imgs = cv2.imreadmulti(inp)
#    imgarr = []
#    prearr = []
#    d = []
#
#    for ind,img in enumerate(imgs):
#        dim = img.shape
#        if len(dim) == 3:
#            # Converting color image to grayscale image
#            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#        height = img.shape[0]
#        width = img.shape[1]
#        heightTenPerc = height // 10
#        widthTenPerc = width // 10
#        blur = cv2.medianBlur(img,3)
#
#        #Binarization of image - Make it strictly black or white 0 or 255
#        pre = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
#        hierarcy,boxes = detectRegions(pre)
#        boxCoords = [[int(box[0]),int(box[1]),int(box[0] + box[2]),
#                      int(box[1] + box[3])] for box in boxes]   ## parameter of each word in
#        heights = [(box[3] - box[1]) for box in boxCoords]  ## list of height of all words in the page
#        widths = [(box[2] - box[0]) for box in boxCoords]
#        mdnWd = np.median(widths)
#        mdnHt = np.median(heights)
#        mdnWd_r = mdnWd / width
#        mdnHt_r = mdnHt / height
#
#        expandedBoxes = [[box[0] - (3 * int(mdnWd)),
#                          box[1],
#                          box[2] + (3 * int(mdnWd)),
#                          box[3]] for i,box in enumerate(boxCoords)]
#
#        expandedBoxes = [box for box in expandedBoxes if box[3] - box[1] >= mdnHt]
#        boxes,smallRegions = combineBoxesNew(expandedBoxes,
#                                             height,width,
#                                             {"width":mdnWd,
#                                              "height":mdnHt})
#
#        cpy1 = pre.copy()
#        cpy = np.stack([cpy1,cpy1,cpy1],axis = 2)
#        threshHt = min(3 * mdnHt, 100)

#        sboxes = sorted(boxes,key = operator.itemgetter(1))
#
#        while len(sboxes) > 0:
#            ref = sboxes[0]
#            colluntil = 0
#            for i in range(1,11):
#                if len(sboxes) > i + 1:
#                    box = sboxes[i]
#                    isColl = isHCollinear(ref,box)
#                    if isColl:
#                        colluntil += 1
#                    else:
#                        break
#            if colluntil >= minColsForLnItmTbl:
#                mintop = min([box[1] for box in sboxes[:colluntil]])
#                cv2.line(cpy,(0,mintop),(height,mintop),(0,255,0),thickness=2)
#
#            del sboxes[:colluntil + 1]
#
#        for boxId,box in enumerate(boxes):
#            cv2.rectangle(cpy,(box[0],box[1]),
#                          (box[2],box[3]),
#                          (255,255,0),3)
#
#        outpath = os.path.join(outfolder, os.path.split(inp)[1] + "_" + str(ind) + ".TIF")
#        cv2.imwrite(outpath,cpy)


#cnt = 0
#filepaths = []
#rerun = True
#
#for root, subfolder, files in os.walk(inp):
#    for fileName in files:
#        outdir = root.replace(inp,out)
#        os.makedirs(outdir, exist_ok = True)
#        inppath = os.path.join(root,fileName)
#        outpath = os.path.join(outdir,fileName)
#        process = not os.path.exists(outpath + "_outliers.xlsx")
#        barcode_left_diff=[]   #### pybar chnage
#        barcode_top_diff=[]    #### pybar chnage
#        if not rerun:
#            if os.path.isfile(outpath + "_outliers.xlsx"):
#                process = False
#
#        if process:
#            result,imgs = cv2.imreadmulti(inppath)
#            imgarr = []
#            prearr = []
#            d = []
#
#            for ind,img in enumerate(imgs):
#                dim = img.shape
#                if len(dim) == 3:
#                    # Converting color image to grayscale image
#                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#                height = img.shape[0]
#                width = img.shape[1]
#                heightTenPerc = height // 10
#                widthTenPerc = width // 10
#                blur = cv2.medianBlur(img,3)
#
#                #Binarization of image - Make it strictly black or white 0 or 255
#                pre = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
#                hierarcy,boxes = detectRegions(pre)
#                boxCoords = [[int(box[0]),int(box[1]),int(box[0] + box[2]),
#                              int(box[1] + box[3])] for box in boxes]   ## parameter of each word in
#                heights = [(box[3] - box[1]) for box in boxCoords]  ## list of height of all words in the page
#                widths = [(box[2] - box[0]) for box in boxCoords]
#                mdnWd = np.median(widths)
#                mdnHt = np.median(heights)
#                mdnWd_r = mdnWd / width
#                mdnHt_r = mdnHt / height
#
#                expandedBoxes = [[box[0] - (3 * int(mdnWd)),
#                                  box[1],
#                                  box[2] + (3 * int(mdnWd)),
#                                  box[3]] for i,box in enumerate(boxCoords)]
#
#                expandedBoxes = [box for box in expandedBoxes if box[3] - box[1] >= mdnHt]
#                boxes,smallRegions = combineBoxesNew(expandedBoxes,
#                                                     height,width,
#                                                     {"width":mdnWd,
#                                                      "height":mdnHt})
#
#                cpy1 = pre.copy()
#                cpy = np.stack([cpy1,cpy1,cpy1],axis = 2)
#                threshHt = min(3 * mdnHt, 100)
#
#                barx=0   #### pybar chnage
#                bary=0   #### pybar chnage
#                barw=0   #### pybar chnage
#                barh=0   #### pybar chnage
#
#                for boxId,box in enumerate(boxes):
#                    cv2.rectangle(cpy,(box[0],box[1]),
#                                  (box[2],box[3]),
#                                  (0,255,0),3)
#
#                cv2.imwrite(outImage,cpy)
#
