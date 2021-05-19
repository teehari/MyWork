# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 23:08:50 2020

@author: Hari
"""

import json
import pandas as pd
import os

inpAWSFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/AWS_OP"
inpAzFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/analyzelayoutop"
opFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/AzureLayout"

def crAzWords(blocks):
    #Create word list
    words = []
    for block in blocks:
        lines = block["lines"]
        for line in lines:
            lWords = line["words"]
            for lword in lWords:
                word = {}
                word["text"] = lword["text"]
                word["left"] = lword["boundingBox"][0]
                word["top"] = lword["boundingBox"][1]
                word["width"] = lword["boundingBox"][4] - word["left"]
                word["height"] = lword["boundingBox"][5] - word["top"]
                words.append(word)
    return words

def crWords(blocks):
    #Create word list
    words = {}
    for block in blocks:
        blockType = block["BlockType"]
        if blockType == "WORD":
            bb = block["Geometry"]["BoundingBox"]
            words[block["Id"]] = (block["Text"],
                 block["Confidence"],bb["Left"],bb["Top"],
                 bb["Width"],bb["Height"])
    return words

def crKeyVals(blocks,words):
    keys = {}
    for block in blocks:
        blockType = block["BlockType"]
        if blockType == "KEY_VALUE_SET":
            key = {}
            entityType = block["EntityTypes"][0]
            if entityType == "KEY":
                keys[block["Id"]] = key
                relations = block["Relationships"]
                key["confidence"] = block["Confidence"]
                for relation in relations:
                    relType = relation["Type"]
                    if relType == "CHILD":
                        wordIds = relation["Ids"]
                        keyWords = []
                        for wordId in wordIds:
                            keyWords.append(wordId)
                        key["keyWords"] = keyWords
                    elif relType == "VALUE":
                        valueIds = relation["Ids"]
                        values = []
                        for valueId in valueIds:
                            values.append(valueId)
                        key["valueIds"] = values

    values = {}
    for block in blocks:
        blockType = block["BlockType"]
        if blockType == "KEY_VALUE_SET":
            value = {}
            entityType = block["EntityTypes"][0]
            if entityType == "VALUE":
                if "Relationships" in block.keys():
                    values[block["Id"]] = value
                    relations = block["Relationships"]
                    value["confidence"] = block["Confidence"]
                    for relation in relations:
                        relType = relation["Type"]
                        if relType == "CHILD":
                            wordIds = relation["Ids"]
                            valueWords = []
                            for wordId in wordIds:
                                valueWords.append(wordId)
                            value["valueWords"] = valueWords

    keyValues = []
    for key in keys.keys():
        keyValue = {}
        if key in keys.keys():
            if "keyWords" in keys[key].keys():
                keyWords = keys[key]["keyWords"]
                keyVals = []
                for keyWord in keyWords:
                    keyVals.append(words[keyWord][0])
                keyValue["key"] = " ".join(keyVals)
                valueIds = keys[key]["valueIds"]
                vals = []
                for valueId in valueIds:
                    if valueId in values.keys():
                        if "valueWords" in values[valueId].keys():
                            valueWords = values[valueId]["valueWords"]
                            for valueWord in valueWords:
                                if valueWord in words.keys():
                                    vals.append(words[valueWord][0])
                keyValue["value"] = " ".join(vals)
                keyValues.append(keyValue)
    return keyValues

def crTables(blocks,words):
    cells = []
    for block in blocks:
        blockType = block["BlockType"]
        if blockType == "CELL":
            if "Relationships" in block.keys():
                cell = {}
                cell["rowIndex"] = block["RowIndex"]
                cell["colIndex"] = block["ColumnIndex"]
                relations = block["Relationships"]
                tabWords = []
                for relation in relations:
                    if relation["Type"] == "CHILD":
                        wordIds = relation["Ids"]
                        tabWords.extend(wordIds)
                try:
                    cell["cellValue"] = " ".join([words[wordId][0] for wordId in wordIds])
                except:
                    cell["cellValue"] = " "
                cells.append(cell)
    return cells

labels = []

for root, subFolder, fileNames in os.walk(inpAWSFolder):
    for fileName in fileNames:
        
        #Get AWS O/p
        folderName = os.path.split(root)[1]
        opPath = os.path.join(opFolder,folderName)
        os.makedirs(opPath,exist_ok = True)
        inpFilePath = os.path.join(root,fileName)
        extn = os.path.splitext(fileName)[1]
        extn = extn.upper()
        fileNameWoExtn = os.path.splitext(fileName)[0]
        
        #Get Azure O/P
        azInpFileName = os.path.join(inpAzFolder,folderName + "_" + fileNameWoExtn + ".TIFF.ocr.json")

        if os.path.exists(azInpFileName):
        
            labelFile = fileName + ".labels.json"
            if not os.path.exists(labelFile):

                #Read AWS O/P file
                fObj = open(inpFilePath,"r")
                jsonText = fObj.read()
                fObj.close()
                jsonObj = json.loads(jsonText)

                #Read Azure O/P file
                fObj = open(azInpFileName,"r")
                jsonText = fObj.read()
                fObj.close()
                azJsonObj = json.loads(jsonText)


                #Read AWS O/P
                if isinstance(jsonObj,list):
                    blocks = jsonObj
                elif isinstance(jsonObj,dict):
                    blocks = jsonObj["Blocks"]

                #Create a word dictionary, keyvalues, table values from AWS O/p
                words = crWords(blocks)
                keyValues = crKeyVals(blocks,words)
                tables = crTables(blocks,words)

                #Read Azure O/P
                azBlocks = azJsonObj["analyzeResult"]["readResults"]

                #Create word dictionary Azure
                azWords = crAzWords(azBlocks)

                if len(keyValues) > 0:
                    dfKeyVal = pd.DataFrame(keyValues)
                    dfKeyVal.to_csv(outFilePathKeyVal,index = False)
                    keys = list(dfKeyVal["key"])
                    keys = list(set([key.upper() for key in keys]))
                    labels.extend(keys)
                    labels = list(set(labels))
                if len(tables) > 0:
                    dfTables = pd.DataFrame(tables)
                    dfTables.to_csv(outFilePathTable,index = False)









