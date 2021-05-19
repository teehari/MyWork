# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 22:11:13 2020

@author: Hari
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:14:05 2020

@author: Hari
"""
import os
import cv2
import json
import pandas as pd

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

def findWordsClose(row,df):

    pixelThresh = .03
    sdPixelThresh = .5

    #find words above
    word1ab = ""
    word2ab = ""
    word3ab = ""
    word4ab = ""
    word5ab = ""
    d1ab = 0
    d2ab = 0
    d3ab = 0
    d4ab = 0
    d5ab = 0

    top = row["top"] - pixelThresh
    dffilt = df[(df["bottom"] >= top) & (df["bottom"] < row["top"])]
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [row["left"],top,row["right"],row["bottom"]]
        rect2 = [j["left"],j["top"],j["right"],j["bottom"]]
        overlap = isOverlap(rect1,rect2)
        if overlap:
            if cnt == 0:
                word1ab = j["word"]
                d1ab = j["top"] - row["top"]
            elif cnt == 1:
                word2ab = j["word"]
                d2ab = j["top"] - row["top"]
            elif cnt == 2:
                word3ab = j["word"]
                d3ab = j["top"] - row["top"]
            elif cnt == 3:
                word4ab = j["word"]
                d4ab = j["top"] - row["top"]
            elif cnt == 4:
                word5ab = j["word"]
                d5ab = j["top"] - row["top"]
            else:
                break
            cnt += 1

    #find words below
    word1be = ""
    word2be = ""
    word3be = ""
    word4be = ""
    word5be = ""
    d1be = 0
    d2be = 0
    d3be = 0
    d4be = 0
    d5be = 0

    bottom = row["bottom"] + pixelThresh
    dffilt = df[(df["top"] <= bottom) & (df["top"] > row["bottom"])]
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [row["left"],row["top"],row["right"],bottom]
        rect2 = [j["left"],j["top"],j["right"],j["bottom"]]
        overlap = isOverlap(rect1,rect2)
        if overlap:
            if cnt == 0:
                word1be = j["word"]
                d1be = j["top"] - row["top"]
            elif cnt == 1:
                word2be = j["word"]
                d2be = j["top"] - row["top"]
            elif cnt == 2:
                word3be = j["word"]
                d3be = j["top"] - row["top"]
            elif cnt == 3:
                word4be = j["word"]
                d4be = j["top"] - row["top"]
            elif cnt == 4:
                word5be = j["word"]
                d5be = j["top"] - row["top"]
            else:
                break
            cnt += 1

    #find words left
    word1lf = ""
    word2lf = ""
    word3lf = ""
    word4lf = ""
    word5lf = ""
    d1lf = 0
    d2lf = 0
    d3lf = 0
    d4lf = 0
    d5lf = 0

    left = row["left"] - sdPixelThresh
    dffilt = df[(df["right"] >= left) & (df["right"] < row["left"])]
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [left,row["top"],row["right"],row["bottom"]]
        rect2 = [j["left"],j["top"],j["right"],j["bottom"]]
        overlap = isOverlap(rect1,rect2)
        if overlap:
            if cnt == 0:
                word1lf = j["word"]
                d1lf = j["left"] - row["left"]
            elif cnt == 1:
                word2lf = j["word"]
                d2lf = j["left"] - row["left"]
            elif cnt == 2:
                word3lf = j["word"]
                d3lf = j["left"] - row["left"]
            elif cnt == 3:
                word4lf = j["word"]
                d4lf = j["left"] - row["left"]
            elif cnt == 4:
                word5lf = j["word"]
                d5lf = j["left"] - row["left"]
            else:
                break
            cnt += 1


    #find words right
    word1rg = ""
    word2rg = ""
    word3rg = ""
    word4rg = ""
    word5rg = ""
    d1rg = 0
    d2rg = 0
    d3rg = 0
    d4rg = 0
    d5rg = 0

    right = row["right"] + sdPixelThresh
    dffilt = df[(df["left"] <= right) & (df["left"] > row["right"])]
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [row["left"],row["top"],right,row["bottom"]]
        rect2 = [j["left"],j["top"],j["right"],j["bottom"]]
        overlap = isOverlap(rect1,rect2)
        if overlap:
            if cnt == 0:
                word1rg = j["word"]
                d1rg = j["left"] - row["left"]
            elif cnt == 1:
                word2rg = j["word"]
                d2rg = j["left"] - row["left"]
            elif cnt == 2:
                word3rg = j["word"]
                d3rg = j["left"] - row["left"]
            elif cnt == 3:
                word4rg = j["word"]
                d4rg = j["left"] - row["left"]
            elif cnt == 4:
                word5rg = j["word"]
                d5rg = j["left"] - row["left"]
            else:
                break
            cnt += 1

    return pd.Series([word1ab,word2ab,word3ab,word4ab,word5ab,
                      d1ab,d2ab,d3ab,d4ab,d5ab,
                      word1be,word2be,word3be,word4be,word5be,
                      d1be,d2be,d3be,d4be,d5be,
                      word1lf,word2lf,word3lf,word4lf,word5lf,
                      d1lf,d2lf,d3lf,d4lf,d5lf,
                      word1rg,word2rg,word3rg,word4rg,word5rg,
                      d1rg,d2rg,d3rg,d4rg,d5rg])


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
    page = pages[ind]
    lines = page["lines"]
    width = page["width"]
    height = page["height"]
    for line in lines:
        words = line["words"]
        for word in words:
            wordDic = {}
            bbs = word["boundingBox"]
            bbs = [bbs[0]/width,bbs[1]/height,bbs[2]/width,bbs[3]/height,
                   bbs[4]/width,bbs[5]/height,bbs[6]/width,bbs[7]/height]
            wordDic["word"] = word["text"]
            wordDic["left"] = min(bbs[0],bbs[6])
            wordDic["top"] = min(bbs[1],bbs[3])
            wordDic["right"] = max(bbs[2],bbs[4])
            wordDic["bottom"] = max(bbs[5],bbs[7])
            wordDic["page"] = ind + 1
            wordDic["filename"] = fileName
            allwords.append(wordDic)

    df = pd.DataFrame(allwords)
    dfsort = df.copy()
    dfsort = dfsort.sort_values(["top","left"],ascending = (True,True))
    dsort = dfsort.to_dict()
    df[["W1Ab","W2Ab","W3Ab","W4Ab","W5Ab","d1Ab","d2Ab","d3Ab","d4Ab","d5Ab",
        "W1Be","W2Be","W3Be","W4Be","W5Be","d1Be","d2Be","d3Be","d4Be","d5Be",
        "W1Lf","W2Lf","W3Lf","W4Lf","W5Lf","d1Lf","d2Lf","d3Lf","d4Lf","d5Lf",
        "W1Rg","W2Rg","W3Rg","W4Rg","W5Rg","d1Rg","d2Rg","d3Rg","d4Rg","d5Rg"
        ]] = df.apply(findWordsClose,args=(dfsort,),axis = 1)
    if dfAll.shape[0] == 0:
        dfAll = df
    else:
        dfAll = dfAll.append(df)
    df = None

import time
t = str(time.time())
dfAll.to_excel("findWordsNearMe_" + t + ".xlsx", index = False)



