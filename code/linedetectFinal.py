# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:14:05 2020

@author: Hari
"""

import os
import cv2
import numpy as np
import traceback

def findZeroPattern(vals):
    binaryVals = vals // 255
    arr1 = np.concatenate(([0],binaryVals))
    arr2 = np.concatenate((binaryVals,[0]))
    ptnVals = np.bitwise_and(arr1,arr2)[1:]

    iszero = np.concatenate(([0], np.equal(ptnVals, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

def findDenseZeros(vals):
    limit = 200
    perc = 0.5

    binaryVals = vals // 255
    ranges = []
    l = binaryVals.shape[0]
    r = l % limit
    q = l // limit
    if r > 1:
        q = q + 1
    for i in range(q):
        lbound = i * limit
        ubound = (i+1) * limit
        arr = binaryVals[lbound:ubound]
        c = np.sum(arr)

        if (1 - (c / limit)) >= perc:
            ranges.append((lbound,ubound))
    return ranges

src = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\images\test"

for fileName in os.listdir(src):

    if 1 == 1:
        fullpath = os.path.join(src,fileName)
        org = cv2.imread(fullpath)
        img = cv2.imread(fullpath,0)
        blur = cv2.medianBlur(img,3)
        thresh = 150

        #Binarization of image - Make it strictly black or white 0 or 255
        pre = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        cpy1 = org.copy()
        height = img.shape[0]
        width = img.shape[1]
        vlines = []
        hlines = []

        #Identify vertical lines
        for i in range(width):
            single = pre[:,i:i+1][:,0]

            if len(single) > 0:
                vLines1 = findZeroPattern(single)
                for line in vLines1:
                    if line[1] - line[0] >= thresh:
                        cv2.line(cpy1,(i,line[0]),(i,line[1]),(0,255,0))
                        rectangle = (i,line[0],i,line[1])
                        vlines.append(rectangle)

        #Identify horizontal lines
        for i in range(height):
            single = pre[i:i+1,:][0]
            if len(single) > 0:
                hLines1 = findZeroPattern(single)
                for line in hLines1:
                    if line[1] - line[0] >= thresh:
                        cv2.line(cpy1,(line[0],i),(line[1],i),(0,0,255))
                        rectangle = (line[0],i,line[1],i)
                        hlines.append(rectangle)
        cv2.imwrite(os.path.join(src, "line1_" + fileName),cpy1)




