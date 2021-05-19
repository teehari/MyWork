# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:14:05 2020

@author: Hari
"""

import os
import cv2
import numpy as np
import traceback

#from skimage.transform import hough_line, hough_line_peaks
#from skimage.feature import canny
#from skimage import data

tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 360)
maxBorder = 50

def group_consecutivezeros(vals, index, thresh = 100, step = 0):
    """Return list of consecutive lists of numbers from vals (number list)."""
    run = []
    result = []
    for indx,v in enumerate(vals):
        if (int(v) == 0):
            run.append(indx)
        else:
            if len(run) >= thresh:
                result.append((index,run[0],indx))
            run = []
    return result

def findConsecZeros(vals):
    iszero = np.concatenate(([0], np.equal(vals, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

def findZeroPattern(vals):
    binaryVals = vals // 255
    arr1 = np.concatenate(([0],binaryVals))
    arr2 = np.concatenate((binaryVals,[0]))
    ptnVals = np.bitwise_and(arr1,arr2)[1:]

    iszero = np.concatenate(([0], np.equal(ptnVals, 0).view(np.int8), [0]))
#    iszero = np.equal(ptnVals, 0).view(np.int8)
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

src = r"D:\Invoice Data Extraction\TAPP 3.0\findlines.tif"

def findDenseZeros(vals):
    limit = 200
    perc = 0.7
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
#        c = Counter(arr)
#        print(arr)
        c = np.sum(arr)

        if (1 - (c / limit)) >= perc:
#            print(Counter(arr))
            ranges.append((lbound,ubound))
    return ranges

#import re

def findLines(img, org, thresh = 100):
    cpy = org.copy()
    height = img.shape[0]
    width = img.shape[1]
    vlines = []
    hlines = []
#    ptn = "[0]{" + str(thresh) + ",}"
    for i in range(width):
        single = img[:,i:i+1][:,0]
#        lsingle = list(single)
#        lsingle = [str(l) for l in lsingle]
#        ssingle = "".join(lsingle)
#        for obj in re.finditer(ptn,ssingle):
#            print("pattern found vertical")
#            low = obj.span(0)[0]
#            high = obj.span(0)[0]
#            cv2.line(cpy,(i,low),(i,high),(0,255,0),2)
#            rectangle = (i,low,i,high)
#            vlines.append(rectangle)

        if len(single) > 0:
#            lines = group_consecutivezeros(single, i, thresh)
#            potlines = findConsecZeros(single)
            potlines = findZeroPattern(single)
            if len(potlines) < 1000:
                potlines = findDenseZeros(single)
            if len(potlines) > 0:
                for line in potlines:
                    if line[1] - line[0] >= thresh:
#                        cv2.line(cpy,(i,line[1]),(i,line[2]),(0,255,0))
#                        rectangle = (line[0],line[1],line[0],line[2])
                        cv2.line(cpy,(i,line[0]),(i,line[1]),(0,255,0))
                        rectangle = (i,line[0],i,line[1])
                        vlines.append(rectangle)
    for i in range(height):
        single = img[i:i+1,:][0]
#        lsingle = list(single)
#        lsingle = [str(l) for l in lsingle]
#        ssingle = "".join(lsingle)
#        for obj in re.finditer(ptn,ssingle):
#            low = obj.span(0)[0]
#            high = obj.span(0)[0]
#            cv2.line(cpy,(low,i),(high,1),(0,255,0),2)
#            rectangle = (low,i,high,i)
#            hlines.append(rectangle)
        if len(single) > 0:
#            lines = group_consecutivezeros(single.T, i, thresh)
#            potlines = findConsecZeros(single)
            potlines = findZeroPattern(single)
            if len(potlines) < 1000:
                potlines = findDenseZeros(single)
            if len(potlines) > 0:
                for line in potlines:
                    if line[1] - line[0] >= thresh:
#                        cv2.line(cpy,(line[1],i),(line[2],i),(0,0,255))
#                        rectangle = (line[1],line[0],line[2],line[0])
                        cv2.line(cpy,(line[0],i),(line[1],i),(0,0,255))
                        rectangle = (line[0],i,line[1],i)
                        hlines.append(rectangle)
    return vlines,hlines, cpy

for fileName in os.listdir(src):
    fullpath = os.path.join(src,fileName)
#    fullpath = r"D:\Invoice Data Extraction\Sample_Invoices\Invoices\Flipkart\Arun_Co\Processed\20190116134731565_86_2.TIFF"
    org = cv2.imread(fullpath)
    img = cv2.imread(fullpath,0)
    blur = cv2.medianBlur(img,3)
#    blur = cv2.GaussianBlur(img, (3, 3), 0)
    #Binarization of image - Make it strictly black or white 0 or 255
    pre = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    vlines,hlines,cpy = findLines(pre,org)
    cv2.imwrite(os.path.join(src, "line_" + fileName),cpy)

#    kernel = np.ones((5,5), np.uint8)
#    img_erosion = cv2.erode(img, kernel, iterations=1)
#    img_dilation = cv2.dilate(img_erosion, kernel, iterations=1)
#
#    height = img.shape[0]
#    width = img.shape[1]
#
#    regions, boxes = detectRegions(img)
##    regions, boxes = detectRegions(blur)
##    regions, boxes = detectRegions(img_erosion)
##    cpy = removeOutliers(boxes)
#    boxCoords = [[int(box[0]),int(box[1]),int(box[0] + box[2]),
#                  int(box[1] + box[3])] for box in boxes]
#    heights = [(box[3] - box[1]) for box in boxCoords]
#    widths = [(box[2] - box[0]) for box in boxCoords]
#    mdnWd = np.median(widths)
#    mdnHt = np.median(height)
#
##    expandedBoxes = [[box[0] - (2 * int(mdnWd)),box[1],
##                      box[2] + (2 * int(mdnWd)),
##                      box[3]] for i,box in enumerate(boxCoords)]
#    expandedBoxes = [[box[0] - (3 * int(mdnWd)),
#                      box[1],
#                      box[2] + (3 * int(mdnWd)),
#                      box[3]] for i,box in enumerate(boxCoords)]
#    expCopy = sorted(expandedBoxes, key = lambda k: (k[0],k[1],k[2],k[3]))
#    lines = [box for box in expCopy if ((box[2] - box[0]) > 100) and ((box[3] - box[1]) <= 10)]
#
#    expandedBoxes = [[box[0],
#                      box[1] - (2 * int(mdnHt)),
#                      box[2],
#                      box[3] + (2 * int(mdnHt))] for i,box in enumerate(boxCoords)]
#    lines2 = [box for box in expCopy if ((box[3] - box[1]) > 100) and ((box[2] - box[0]) <= 10)]
#    lines.extend(lines2)
#    for box in lines:
#        cv2.rectangle(org,(box[0],box[1]),(box[2],box[3]),(0,0,255),2)
#    cpy = org.copy()
#    for box in expCopy:
#        cv2.rectangle(cpy,(box[0],box[1]),(box[2],box[3]),(0,0,255),2)
#    cv2.imwrite(os.path.join(src, "line_" + fileName),org)
#    cv2.imwrite(os.path.join(src, "all_" + fileName),org)
#    cv2.imwrite(os.path.join(src, "blur_" + fileName),blur)
    
#    binary = cv2.threshold(blur,210,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#    h, theta, d = hough_line(binary, theta=tested_angles)
#    edges = applyCanny2(blur,0.5)
#    lines = cv2.HoughLines(edges,1,np.pi/180, 190)
#    for r, theta in lines[0]:
#        a = np.cos(theta)
#        b = np.sin(theta)
#        x0 = a * r
#        y0 = b * r
#        x1 = int(x0 + 1000*(-b))
#        y1 = int(y0 + 1000*(a))
#        x2 = int(x0 - 1000*(-b))
#        y2 = int(y0 - 1000*(a))
#        cv2.line(org, (x1,y1), (x2,y2), (0,0,255),2)
#    cv2.imwrite(os.path.join(src, "line_" + fileName),org)

