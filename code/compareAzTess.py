# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 23:42:37 2020

@author: Hari
"""

imgpath = "D:\\Invoice Data Extraction\\TAPP 3.0\\DataTagging\\DataTagging\\Processed\\Format_24\Doc_2207.tiff"
azurerespath = "D:\\Invoice Data Extraction\\TAPP 3.0\\DataTagging\\analyzelayoutop\\Format_24_Doc_2207.TIFF.ocr.json"

import cv2
import json
import pandas as pd
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR5.0alpha\\tesseract.exe"

inpAzFolder = r"D:\Invoice Data Extraction\TAPP 3.0\DataTagging\analyzelayoutop"
inpOrgFolder = r"D:\Invoice Data Extraction\TAPP 3.0\DataTagging\DataTagging\Processed"
outfile = "d:\\compare.csv"

if os.path.isfile(outfile):
    os.remove(outfile)

def compareText(row):
    if str(row["text"]).lower().strip() == str(row["aztext"]).lower().strip():
        return "E"
    elif str(row["text"]).lower().strip() == "-1":
        return "A"
    elif str(row["aztext"]).lower().strip() == "-1":
        return "T"
    elif str(row["text"]).lower().strip() != str(row["aztext"]).lower().strip():
        return "D"

cnt = 0
import time
t = time.time()
for fileName in os.listdir(inpAzFolder):
    print(time.time() - t)
    t = time.time()
    print(fileName,cnt + 1)
    cnt += 1
    imageFormatName = fileName.split(".ocr.json")[0]
    formatName = imageFormatName.split("_Doc")[0]
    docName = imageFormatName.split(formatName + "_")[1]
    imageFolderName = os.path.join(inpOrgFolder,formatName)
    imgpath = os.path.join(imageFolderName,docName)
    if os.path.isfile(imgpath):
        img = cv2.imread(imgpath,0)
        tessocr = pytesseract.image_to_data(imgpath,
                                            output_type="data.frame")
        tessocr = tessocr[tessocr["conf"] != -1]
        tessocr = tessocr[["left","top","width","height","text","page_num"]]
        pageNos = list(tessocr["page_num"].unique())
        ocr = tessocr.copy()
        ocr["azleft"] = -1
        ocr["aztop"] = -1
        ocr["azwidth"] = -1
        ocr["azheight"] = -1
        ocr["aztext"] = "-1"
        ocr["pageNo"] = -1
        ocr["format"] = formatName
        ocr["fileName"] = docName
        ocr = ocr.reset_index()

        f = open(os.path.join(inpAzFolder,fileName),"r")
        val = f.read()
        f.close()
        azureop = json.loads(val)

        results = azureop["analyzeResult"]["readResults"]
        for pageNo in pageNos:
            pageOcr = tessocr[tessocr["page_num"] == pageNo]
            lines = results[pageNo - 1]["lines"]
            azop = {}
            azop["azleft"] = []
            azop["aztop"] = []
            azop["azwidth"] = []
            azop["azheight"] = []
            azop["aztext"] = []
            azop["pageNo"] = pageNo
            azop["format"] = formatName
            azop["fileName"] = docName
            ocr["pageNo"] = pageNo

            for line in lines:
                words = line["words"]
                for word in words:
                    bb = word["boundingBox"]
                    text = word["text"]
                    left = bb[0]
                    top = bb[1]
                    width = bb[2] - left
                    height = bb[5] - top
                    azop["aztext"].append(text)
                    azop["azleft"].append(left)
                    azop["aztop"].append(top)
                    azop["azwidth"].append(width)
                    azop["azheight"].append(height)

            azocr = pd.DataFrame(azop)
            selRows = []
            for ind, row in ocr.iterrows():
                for azind, azrow in azocr.iterrows():
                    diff = abs(row["left"]-azrow["azleft"]) + abs(row["top"]-azrow["aztop"])
                    if (diff <= 20):
                        ocr.iloc[ind,ocr.columns.get_loc("azleft")] = azrow["azleft"]
                        ocr.iloc[ind,ocr.columns.get_loc("aztop")] = azrow["aztop"]
                        ocr.iloc[ind,ocr.columns.get_loc("azwidth")] = azrow["azwidth"]
                        ocr.iloc[ind,ocr.columns.get_loc("azheight")] = azrow["azheight"]
                        ocr.iloc[ind,ocr.columns.get_loc("aztext")] = azrow["aztext"]
                        selRows.append(azind)
                        break

        azrem = azocr.copy()
        azrem = azrem.drop(selRows)
        azrem["left"] = -1
        azrem["top"] = -1
        azrem["width"] = -1
        azrem["height"] = -1
        azrem["text"] = -1
        ocr = ocr.append(azrem)
        ocr["diffType"] = ""
        ocr["diffType"] = ocr.apply(lambda row: compareText(row), axis = 1)
        ocr = ocr[ocr["diffType"] != "E"]
        if os.path.isfile(outfile):
            ocr.to_csv(outfile,index = False,mode = "a",
                       header = False)
        else:
            ocr.to_csv(outfile,index = False)



