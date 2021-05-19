# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:14:05 2020

@author: Hari
"""
import os
import cv2
import numpy as np
import json
import pandas as pd

def findZeroPattern(vals):
    binaryVals = vals // 255
    arr1 = np.concatenate(([0],binaryVals))
    arr2 = np.concatenate((binaryVals,[0]))
    ptnVals = np.bitwise_and(arr1,arr2)[1:]

    iszero = np.concatenate(([0], np.equal(ptnVals, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

def findLines(arr):

    height = arr.shape[0]
    width = arr.shape[1]
    vlines = []
    hlines = []
    thresh = 150

    #Identify vertical lines
    for i in range(width):
        single = arr[:,i:i+1][:,0]

        if len(single) > 0:
            vLines1 = findZeroPattern(single)
            for line in vLines1:
                if line[1] - line[0] >= thresh:
                    coord = (i,line[0],i,line[1])
                    vlines.append(coord)

    #Identify horizontal lines
    for i in range(height):
        single = arr[i:i+1,:][0]
        if len(single) > 0:
            hLines1 = findZeroPattern(single)
            for line in hLines1:
                if line[1] - line[0] >= thresh:
                    coord = (line[0],i,line[1],i)
                    hlines.append(coord)
    return vlines,hlines

def sortHline(val):
    return val[1],val[3]

def sortVline(val):
    return val[0],val[2]

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

def findLinesClose(row,hlines,vlines):

    pixelThresh = .03
    isAbove = 0
    lenAbove = 0
    isBelow = 0
    lenBelow = 0
    isLeft = 0
    lenLeft = 0
    isRight = 0
    lenRight = 0

    wordBB = [row["left"],row["top"],row["right"],row["bottom"]]

    #find line above
    hlines.sort(key = sortHline)

    for hline in hlines:
        adjustedY = hline[1] + pixelThresh
        rect1 = (hline[0],hline[1],hline[2],adjustedY)
        overlap = isOverlap(rect1,wordBB)
        if overlap:
            isAbove = 1
            lenAbove = hline[2] - hline[0]
            break

    #find Line below
    hlines.sort(key = sortHline, reverse = True)
    for hline in hlines:
        adjustedY = hline[1] - pixelThresh
        rect1 = (hline[0],adjustedY,hline[2],hline[1])
        overlap = isOverlap(rect1,wordBB)
        if overlap:
            isBelow = 1
            lenBelow = hline[2] - hline[0]
            break

    #Find line Left
    vlines.sort(key = sortVline)
    for vline in vlines:
        adjustedX = vline[0] + pixelThresh
        rect1 = (vline[0],vline[1],adjustedX,vline[3])
        overlap = isOverlap(rect1,wordBB)
        if overlap:
            isLeft = 1
            lenLeft = vline[3] - vline[1]
            break

    #Find Line Right
    vlines.sort(key = sortVline, reverse = True)
    for vline in vlines:
        adjustedX = vline[0] - pixelThresh
        rect1 = (adjustedX,vline[1],vline[0],vline[3])
        overlap = isOverlap(rect1,wordBB)
        if overlap:
            isRight = 1
            lenRight = vline[3] - vline[1]
            break
    return pd.Series([isAbove, lenAbove, isBelow, lenBelow, isLeft,
            lenLeft, isRight, lenRight])

imgsrc = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\images\Hari\Doc_8786.TIF"
ocrsrc = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\ocrs\Hari\Doc_8786.TIF.ocr.json"
fileName = os.path.split(imgsrc)[1]
ret, imgs = cv2.imreadmulti(imgsrc)

f = open(ocrsrc,"r")
content = f.read()
f.close()

obj = json.loads(content)
pages = obj["analyzeResult"]["readResults"]

dfAll = pd.DataFrame()

for ind,img in enumerate(imgs):
    allwords = []
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(img,3)
    pre = cv2.threshold(blur, 210, 255,
                        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    vlines, hlines = findLines(pre)
    height = pre.shape[0]
    width = pre.shape[1]

    hlines = [(hline[0] / width,hline[1] / height,hline[2] / width,hline[3] / height) for hline in hlines]
    vlines = [(vline[0] / width,vline[1] / height,vline[2] / width,vline[3] / height) for vline in vlines]

    page = pages[ind]
    lines = page["lines"]
    for line in lines:
        words = line["words"]
        for word in words:
            wordDic = {}
            bbs = word["boundingBox"]
            bbs = [bbs[0]/width,bbs[1]/height,bbs[2]/width,bbs[3]/height,
                   bbs[4]/width,bbs[5]/height,bbs[6]/width,bbs[7]/height]
            bb = [min(bbs[0],bbs[6]),min(bbs[1],bbs[3]),
                  max(bbs[2],bbs[4]),max(bbs[5],bbs[7])]
            wordDic["word"] = word["text"]
            wordDic["left"] = min(bbs[0],bbs[6])
            wordDic["top"] = min(bbs[1],bbs[3])
            wordDic["right"] = max(bbs[2],bbs[4])
            wordDic["bottom"] = max(bbs[5],bbs[7])
            wordDic["page"] = ind + 1
            wordDic["filename"] = fileName
            allwords.append(wordDic)

    df = pd.DataFrame(allwords)
    df[["lineTop","topLineLen","lineDown","downLineLen","lineLeft",
        "leftLineLen","lineRight","rightLineLen"]] = df.apply(findLinesClose,
        args=(hlines,vlines),axis = 1)
    if dfAll.shape[0] == 0:
        dfAll = df
    else:
        dfAll = dfAll.append(df)
    df = None

import time
t = str(time.time())
dfAll.to_excel("findLinesNearMe_" + t + ".xlsx", index = False)

