# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 15:08:45 2020

@author: Hari
"""

import json
import pandas as pd
import os
import time

inpFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/AWS_OP"
opFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/AWS_Format_OP"
lblFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging"

def crWords(blocks):
    #Create word list
    words = {}
    for block in blocks:
        blockType = block["BlockType"]
        if blockType == "WORD":
            words[block["Id"]] = (block["Text"],block["Confidence"])
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

for root, subFolder, fileNames in os.walk(inpFolder):
    for fileName in fileNames:
        folderName = os.path.split(root)[1]
        opPath = os.path.join(opFolder,folderName)
        os.makedirs(opPath,exist_ok = True)
        inpFilePath = os.path.join(root,fileName)
        extn = os.path.splitext(fileName)[1]
        extn = extn.upper()
        fileNameWoExtn = extn = os.path.splitext(fileName)[0]
        opFileNameKeyVal = fileNameWoExtn + "_keyvaluepairs.csv"
        outFilePathKeyVal = os.path.join(opPath,opFileNameKeyVal)
        opFileNameTable = fileNameWoExtn + "_tables.csv"
        outFilePathTable = os.path.join(opPath,opFileNameTable)
        if not os.path.exists(opFileNameTable):
            fObj = open(inpFilePath,"r")
            jsonText = fObj.read()
            fObj.close()
            jsonObj = json.loads(jsonText)
            if isinstance(jsonObj,list):
                blocks = jsonObj
            elif isinstance(jsonObj,dict):
                blocks = jsonObj["Blocks"]
            words = crWords(blocks)
            keyValues = crKeyVals(blocks,words)
            tables = crTables(blocks,words)
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

allLabels = {}
allLabels["LabelValues"] = labels

dfLabel = pd.DataFrame(allLabels)
strTimeStamp = str(time.time())
dfLabel.to_csv(os.path.join(lblFolder,"Labels_" + strTimeStamp + ".csv"),
               index = False)



#df = pd.DataFrame(keyValues)
#
#
#print("/n/n",cells)
#
