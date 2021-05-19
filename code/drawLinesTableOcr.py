# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:28:56 2020

@author: Hari
"""
import os
import glob
import cv2
import pandas as pd
import re
import operator
import json

minColsForLnItmTbl = 3

def isHCollinear(rect1, rect2):
    try:
        if (rect1[1] <= rect2[1]) and (rect1[3] >= rect2[1]):
            return True
        elif (rect2[1] <= rect1[1]) and (rect2[3] >= rect1[1]):
            return True
        else:
            return False
    except Exception as e:
        print(e,"isHCollinear")
        return False

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

for ind,inpfile in enumerate(inpfiles):

    inp = inpfile.rstrip(".ocr.json")
    f = open(inpfile,"r")
    content = f.read()
    obj = json.loads(content)
    lines = obj["analyzeResult"]["readResults"][0]["lines"]
    height = obj["analyzeResult"]["readResults"][0]["height"]
    width = obj["analyzeResult"]["readResults"][0]["width"]
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
    df["lineno"] = 0

    sboxes = sorted(boxes,key = operator.itemgetter(1))
    filename = inpfile.rstrip(".TIF.ocr.json")
    filename = os.path.split(filename)[1]
    actualfilename = "_".join(filename.split("_")[0:-1])
    pageno = filename.split("_")[-1]
    img = cv2.imread(inp)
    cpy = img.copy()

    linecnt = 1
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

        if ((colluntil + 1) >= 2):
            mintop = min([box[1] for box in sboxes[:colluntil + 1]])
            maxleft = max([box[0] for box in sboxes[:colluntil + 1]])
            selboxes = sboxes[:colluntil + 1]
            noOfAmts = 0
            lastAmt = 0
            for selbox in selboxes:
                if isAmount(selbox[4]):
                    noOfAmts += 1
                    if selbox[0] == maxleft:
                        lastAmt = 1

            if (noOfAmts >= 1) or (colluntil >= 3):
                cv2.line(cpy,(0,mintop),(width,mintop),(0,255,0),
                         thickness=2)
                for selbox in selboxes:
                    df.loc[(df["left"] == selbox[0]) & 
                           (df["top"] == selbox[1]) & 
                           (df["right"] == selbox[2]) &
                           (df["bottom"] == selbox[3]),["isTableLine"]] = 1
                    df.loc[(df["left"] == selbox[0]) & 
                           (df["top"] == selbox[1]) & 
                           (df["right"] == selbox[2]) &
                           (df["bottom"] == selbox[3]),"noNeighbours"] = colluntil
                    df.loc[(df["left"] == selbox[0]) & 
                           (df["top"] == selbox[1]) & 
                           (df["right"] == selbox[2]) &
                           (df["bottom"] == selbox[3]),"isLastAmt"] = lastAmt
                    df.loc[(df["left"] == selbox[0]) & 
                           (df["top"] == selbox[1]) & 
                           (df["right"] == selbox[2]) &
                           (df["bottom"] == selbox[3]),["lineno"]] = linecnt
                linecnt += 1

        del sboxes[:colluntil + 1]

#    for boxId,box in enumerate(boxes):
#        cv2.rectangle(cpy,(box[0],box[1]),(box[2],box[3]),
#                      (255,255,0),3)

    outpath = os.path.join(outfolder, filename + ".TIF")
#    print("Out:",outpath)
    cv2.imwrite(outpath,cpy)
    df.to_excel(os.path.join(outfolder, filename + ".xlsx"),
                index = False)



