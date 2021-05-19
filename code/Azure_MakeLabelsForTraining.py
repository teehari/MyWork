# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 21:54:24 2020

@author: Hari
"""

import json
import os
import glob
#import pandas as pd

inpFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/analyzelayoutop"
labelFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/labelop"
jsonFolder = "D:/Invoice Data Extraction/TAPP 3.0/Tagged_JSON/Tagged_JSON"

jsonList = os.listdir(inpFolder)
labeledJsons = []

def readLayouts(layoutJson):
    pageResults = layoutJson["analyzeResult"]["readResults"]
    pages = []
    for pageResult in pageResults:
        lineResults = pageResult["lines"]
        for lineResult in lineResults:
            wordResults = lineResult["words"]

            for wordResult in wordResults:
                page = {}
                page["page"] = pageResult["page"]
                page["text"] = wordResult["text"]
                bBox = wordResult["boundingBox"]
                page["x1"] = bBox[0]
                page["y1"] = bBox[1]
                page["x2"] = bBox[2]
                page["y2"] = bBox[3]
                page["x3"] = bBox[4]
                page["y3"] = bBox[5]
                page["x4"] = bBox[6]
                page["y4"] = bBox[7]
                if page not in pages:
                    pages.append(page)

    return pages

def get_iou(bb1, bb2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bb1 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x, y) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    try:
        assert bb1['x1'] <= bb1['x2']
        assert bb1['y1'] <= bb1['y2']
        assert bb2['x1'] <= bb2['x2']
        assert bb2['y1'] <= bb2['y2']
    except:
        print("Assert issue",bb1,bb2)
        return 0.0

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1['x1'], bb2['x1'])
    y_top = max(bb1['y1'], bb2['y1'])
    x_right = min(bb1['x2'], bb2['x2'])
    y_bottom = min(bb1['y2'], bb2['y2'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
    bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou

def locateLabels(labelPoint, imageWidth, imageHeight, words):

    gx1 = round(labelPoint[0][0] * imageWidth)
    gx3 = round(labelPoint[2][0] * imageWidth)
    gy1 = round(labelPoint[0][1] * imageHeight)
    gy3 = round(labelPoint[2][1] * imageHeight)
    x1 = min(gx1,gx3)
    x2 = max(gx1,gx3)
    y1 = min(gy1,gy3)
    y2 = max(gy1,gy3)
    returnPages = []

    for word in words:
        bb1 = {}
        bb1["x1"] = x1
        bb1["x2"] = x2
        bb1["y1"] = y1
        bb1["y2"] = y2
        mx1 = word["x1"]
        mx2 = word["x3"]
        my1 = word["y1"]
        my2 = word["y3"]
        nx1 = min(mx1,mx2)
        nx2 = max(mx1,mx2)
        ny1 = min(my1,my2)
        ny2 = max(my1,my2)
        bb2 = {}
        bb2["x1"] = nx1
        bb2["x2"] = nx2
        bb2["y1"] = ny1
        bb2["y2"] = ny2
        iou = get_iou(bb1,bb2)
        if iou > .250:
            returnPages.append(word)
    return returnPages

for jsonFile in jsonList:

    inpFile = os.path.join(inpFolder, jsonFile)
    formNum = jsonFile[:jsonFile.upper().find("_DOC")]
    remnant = jsonFile.lstrip(formNum + "_")
    docNum = remnant[:remnant.upper().find(".TIFF")]

    f = open(inpFile,"r")
    layoutJson = json.loads(f.read())
    f.close()

    words = readLayouts(layoutJson)

    labelJsonFile = glob.glob(os.path.join(jsonFolder,formNum + ".json"))
    f = open(labelJsonFile[0],"r")
    labelJson = None
    labeledJson = {}

    for x in f:
        labelJson = json.loads(x)
        fPath = labelJson["content"]
        fName = os.path.split(fPath)[1]
        if docNum in fName:
            break
    f.close()

    documentLabels = {}
    documentLabels["document"] = docNum + ".tiff"

    if labelJson is not None:
        labels = labelJson["annotation"]
        if labels is not None:
            docLabels = []
            documentLabels["labels"] = docLabels
            for label in labels:
                lblText = label["label"][0]
                imgWidth = label["imageWidth"]
                imgHeight = label["imageHeight"]
                labelPoint = label["points"]
                returnPages = locateLabels(labelPoint,imgWidth,imgHeight,words)
                values = []
                docLabel = {}
                docLabel["label"] = lblText
                docLabel["key"] = None
                docLabel["value"] = values
                for returnPage in returnPages:
                    value = {}
                    value["page"] = returnPage["page"]
                    value["text"] = returnPage["text"]
                    boundingBoxes = []
                    boundingBoxes.append(returnPage["x1"])
                    boundingBoxes.append(returnPage["y1"])
                    boundingBoxes.append(returnPage["x2"])
                    boundingBoxes.append(returnPage["y2"])
                    boundingBoxes.append(returnPage["x3"])
                    boundingBoxes.append(returnPage["y3"])
                    boundingBoxes.append(returnPage["x4"])
                    boundingBoxes.append(returnPage["y4"])
                    value["boundingBoxes"] = []
                    value["boundingBoxes"].append(boundingBoxes)
                    values.append(value)
                docLabels.append(docLabel)
    if "labels" in documentLabels.keys():
        jsonText = json.dumps(documentLabels)
        labelFile = os.path.join(labelFolder,jsonFile.rstrip(".ocr.json") + ".labels.json")
        f = open(labelFile,"w")
        f.write(json.dumps(documentLabels))
        f.close()

