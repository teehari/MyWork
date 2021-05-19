# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:35:20 2020

@author: Hari
"""


import json
import pandas as pd
import os
from dateutil.parser import parse
from money_parser import price_str
import re
import string

punct = list(string.punctuation)
punct.remove(".")
punct.remove(",")

inpdir = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\labels"
ocrdir = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\ocrs"
imgdir = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\images"

labellist = list(pd.read_csv("labels.csv")["word"])
labellist = ['invoice','inv','quantity','qty','item','po','number',
             'no.','description','desc','payment','terms','net',
             'days','due','date','dt','reference','vat','tax',
             'total','unit','units','price','amount','amt','bill','ship',
             'billing','shipping','address','payment','reference',
             'value','unit','purchase','ref','uom','weight','wt',
             'services','service','fee','charge','charges','gst',
             'rate','currency','order','discount','subtotal','sub-total',
             'ship','balance','code','period','bank','remittance','account',
             'advice']

def isId(s):
    try:
        if len(s) >= 8:
            if s.isnumeric():
                return True
            else:
                t1 = re.sub('[A-Z][a-z]', 'X',s)
                t2 = re.sub('[0-9]', '0',t1)
                if ("X" in t2) and ("0" in t2):
                    return True
    except:
        return False
    return False

def isAmount_1(s):
    try:
        t1 = re.sub('[0-9]', '0',s)
        if "0" in t1:
            return True
    except:
        return False
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

        ptn9 = "[0-9]{1,3}"

        ptns = [ptn1,ptn2,ptn3,ptn4,ptn5,ptn6,ptn7,ptn8]
        
        for ptn in ptns:
            l = re.findall(ptn,s)
            l1 = [g for g in l if len(g) > 0]
            if len(l1) == 1:
                return True
    except:
        return False
    return False

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except:
        return False

import numpy as np
import cv2

def findZeroPattern(vals):
    binaryVals = vals // 255
    arr1 = np.concatenate(([0],binaryVals))
    arr2 = np.concatenate((binaryVals,[0]))
    ptnVals = np.bitwise_and(arr1,arr2)[1:]

    iszero = np.concatenate(([0], np.equal(ptnVals, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges


def findLines(imgPath,page):

    imgs = cv2.imreadmulti(imgPath)
    img = imgs[1][page]
    blur = cv2.medianBlur(img,3)
    thresh = 150

    #Binarization of image - Make it strictly black or white 0 or 255
    pre = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    height = img.shape[0]
    width = img.shape[1]
    vlines = 0

    #Identify vertical lines
    for i in range(width):
        single = pre[:,i:i+1][:,0]

        if len(single) > 0:
            vLines1 = findZeroPattern(single)
            for line in vLines1:
                if line[1] - line[0] >= thresh:
                    vlines += 1

    return vlines


#Horizontal and Vertical Section numbers
h = 2
v = 1
hvPairs = []

#Create pairs of max X,Y coords for each section
for i in range(h):
    for j in range(v):
        x = (i + 1) * (1 / h)
        y = (j + 1) * (1 / v)
        hvPairs.append((x,y))

pageDensities = []
for root, subfolder, files in os.walk(inpdir):
    if len(files) > 0:

        for fileName in files:
            if fileName[-12:].upper() == ".LABELS.JSON":
                imgName = fileName[:len(fileName)-12]
                ocrFileName = imgName + ".ocr.json"
                actOcrDir = root.replace(inpdir,ocrdir)
                actImgDir = root.replace(inpdir,imgdir)
                imgPath = os.path.join(actImgDir,imgName)

                ocrPath = os.path.join(actOcrDir,ocrFileName)
                f = open(ocrPath,"r")
                ocrText = f.read()
                ocrObj = json.loads(ocrText)
                f.close()

                #Code to identify which are Invoice pages
                lblPath = os.path.join(root,fileName)
                f = open(lblPath,"r")
                lblText = f.read()
                lblObj = json.loads(lblText)
                f.close()

                labels = lblObj["labels"]
                minLblPage = 100000000
                maxLblPage = 0
                pageLabels = {}

                for label in labels:
                    values = label["value"]
                    labelText = label["label"]
                    for value in values:
                        pageNo = value["page"]
                        if pageNo in pageLabels.keys():
                            pageLabels[pageNo].append(labelText)
                        else:
                            pageLabels[pageNo] = [labelText]

                invPages = []
    
                pages = ocrObj["analyzeResult"]["readResults"]
                ocrPages = list(range(1,len(pages)+1))
                (minOcr,maxOcr) = (min(ocrPages),max(ocrPages))
                
                for pageNo in ocrPages:
                    if pageNo in pageLabels.keys():
                        if len(pageLabels[pageNo]) > 1:
                            invPages.append(pageNo)
                        elif pageLabels[pageNo][0] != "barCode":
                            invPages.append(pageNo)

                if len(invPages) > 0:
                    invPages = list(range(min(invPages),max(invPages)+1))

                #Read each word and their coords and add to their corresponding sections
                for pageNum,page in enumerate(pages):
                    labvalues = []
                    #Create a dictionary for each section
                    sections = {}
                    lblsections = {}
                    lblsections["label"] = 0
                    amtsections = {}
                    amtsections["amount"] = 0
                    dtsections = {}
                    dtsections["date"] = 0
                    idsections = {}
                    idsections["id"] = 0
#                    vlines = {}
#                    vlines["vlines"] = findLines(imgPath,pageNum)
                    pageDensity = {}
                    pageDensity["FileName"] = fileName
#                    pageDensity["vlines"] = vlines["vlines"]
                    for i in range(len(hvPairs)):
                        sections[str(i+1)] = 0
                        lblsections[str(i+1)] = 0
                        amtsections[str(i+1)] = 0
                        dtsections[str(i+1)] = 0
                        idsections[str(i+1)] = 0

                    lines = page["lines"]
                    width = page["width"]
                    height = page["height"]
                    totalWords = 0
                    for line in lines:
                        words = line["words"]
                        totalWords += len(words)
                        for word in words:
                            bb = word["boundingBox"]
                            left = round(min(bb[0],bb[6]) / width,2)
                            top = round(min(bb[1],bb[3]) / height,2)
                            text = word["text"].lower().strip()
                            textNoPunct = "".join([" " if g in punct else g for g in text])
                            text = textNoPunct.strip()
                            texts = text.split(" ")
                            for text in texts:
                                for ind, pair in enumerate(hvPairs):
                                    x = pair[0]
                                    y = pair[1]
                                    if ((left <= x)):
                                        sections[str(ind + 1)] += 1
                                        #If Condition to check if the text is in the most common list
                                        if text in labellist:
                                            if text not in labvalues:
                                                lblsections[str(ind + 1)] += 1
                                                lblsections["label"] += 1
                                                labvalues.append(text)
                                        elif is_date(text):
                                            dtsections[str(ind + 1)] += 1
                                            dtsections["date"] += 1
                                        elif isAmount(text):
                                            if ("Doc_11299.TIF" in fileName) and (pageNum == 2):
                                                print(text)
                                            amtsections[str(ind + 1)] += 1
                                            amtsections["amount"] += 1
                                        elif isId(text):
                                            idsections[str(ind + 1)] += 1
                                            idsections["id"] += 1
                                        break
                    pageDensity["page #"] = pageNum + 1
                    if pageNum + 1 in invPages:
                        pageDensity["Inv Page"] = 1
                    else:
                        pageDensity["Inv Page"] = 0
                    pageDensity["Total Words"] = totalWords/1000
                    for section in sections.keys():
                        if totalWords > 0:
                            pageDensity["Section_" + section] = sections[section]/totalWords
                        else:
                            pageDensity["Section_" + section] = 0
                    for lblsection in lblsections.keys():
                        pageDensity["Label_N_" + lblsection] = lblsections[lblsection]
                        pageDensity["Label_N"] = lblsections["label"]
                        if totalWords > 0:
                            pageDensity["Label_" + lblsection] = lblsections[lblsection]/totalWords
                        else:
                            pageDensity["Label_" + lblsection] = 0
                        if totalWords > 0:
                            pageDensity["Label"] = lblsections["label"]/totalWords
                        else:
                            pageDensity["Label"] = 0
                    for amtsection in amtsections.keys():
                        pageDensity["Amount_N_" + amtsection] = amtsections[amtsection]
                        pageDensity["Amount_N"] = amtsections["amount"]
                        if totalWords > 0:
                            pageDensity["Amount_" + amtsection] = amtsections[amtsection]/totalWords
                        else:
                            pageDensity["Amount_" + amtsection] = 0
                        if totalWords > 0:
                            pageDensity["Amount"] = amtsections["amount"] / totalWords
                        else:
                            pageDensity["Amount"] = 0
                    for dtsection in dtsections.keys():
                        pageDensity["Date_N_" + dtsection] = dtsections[dtsection]
                        pageDensity["Date_N"] = dtsections["date"]                        
                        if totalWords > 0:
                            pageDensity["Date_" + dtsection] = dtsections[dtsection]/totalWords
                        else:
                            pageDensity["Date_" + dtsection] = 0
                        if totalWords > 0:
                            pageDensity["Date"] = dtsections["date"] / totalWords
                        else:
                            pageDensity["Date"] = 0
                    for idsection in idsections.keys():
                        pageDensity["Id_N_" + idsection] = idsections[idsection]
                        pageDensity["Id_N"] = idsections["id"]
                        if totalWords > 0:
                            pageDensity["Id_" + idsection] = idsections[idsection]/totalWords
                        else:
                            pageDensity["Id_" + idsection] = 0
                        if totalWords > 0:
                            pageDensity["Id"] = idsections["id"] / totalWords
                        else:
                            pageDensity["Id"] = 0
                    pageDensities.append(pageDensity)

#print("Invoice Page:",invPages)
#print("OCR Pages:",ocrPages)

df = pd.DataFrame(pageDensities)

import time
t = str(round(time.time()))
df.to_excel("pageDensity_" + t + ".xlsx", index = False)
df = df[df["Total Words"] != 0]

nonfeatures = ["FileName","page #","Total Words"]
dfsample = df.drop(nonfeatures, axis = 1)
dfsample_0 = dfsample[dfsample["Inv Page"] == 0]
dfsample_1 = dfsample[dfsample["Inv Page"] == 1]

dftrain_0 = dfsample_0.sample(n = 800)
dftrain_1 = dfsample_1.sample(n = 700)

dftrain = dftrain_0.append(dftrain_1)

trainY = dftrain["Inv Page"]
trainX = dftrain.drop(["Inv Page"], axis = 1)

dftest = df[~df.isin(dftrain)].dropna()
dftest = dftest.drop(nonfeatures, axis = 1)
dftest = dftest.drop(["Inv Page"], axis = 1)

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# Function to perform training with giniIndex. 
def train_using_gini(X_train, y_train): 
  
    # Creating the classifier object 
    clf_gini = DecisionTreeClassifier(criterion = "gini", 
            random_state = 100,max_depth=3, min_samples_leaf=5) 
  
    # Performing training 
    clf_gini.fit(X_train, y_train) 
    return clf_gini 

# Function to perform training with entropy. 
def train_using_entropy(X_train, y_train): 
  
    # Decision tree with entropy 
    clf_entropy = DecisionTreeClassifier( 
            criterion = "entropy", random_state = 100, 
            max_depth = 3, min_samples_leaf = 5) 
  
    # Performing training 
    clf_entropy.fit(X_train, y_train) 
    return clf_entropy

logreg = LogisticRegression()
knn = KNeighborsClassifier(n_neighbors = 3, metric = 'minkowski')

logreg.fit(trainX, trainY)
knn.fit(trainX, trainY)
dtent = train_using_entropy(trainX, trainY)
dtgini = train_using_gini(trainX,trainY)

y1_pred = logreg.predict(dftest)
y2_pred = knn.predict(dftest)
y3_pred = dtent.predict(dftest)
y4_pred = dtgini.predict(dftest)

dftest["inv_page_pred_1"] = y1_pred
dftest["inv_page_pred_2"] = y2_pred
dftest["inv_page_pred_3"] = y3_pred
dftest["inv_page_pred_4"] = y4_pred
dftest["inv_page_pred_5"] = (dftest["Amount_N"] != 0) | ((dftest["Label_N"] >= 5) & (dftest["Date_N"] != 0))
dftest["inv_page_pred_6"] = (dftest["Amount_N_2"] >= 2)
dftest["inv_page_pred_7"] = ((dftest["Label_N"] >= 5) & (dftest["Date_N"] != 0))
dftest["inv_page_pred_8"] = (dftest["Amount_N"] != 0)
#dftest["inv_page_pred_9"] = ((dftest["Amount_N"] >= 3) | ((dftest["Label_N"] >= 5) & (dftest["Date_N"] != 0) & (dftest["Amount_N"] == 0)) | ((dftest["Label_N"] >= 5) & (dftest["Date_N"] != 0) & (dftest["Amount_N"] > 0)))
dftest["inv_page_pred_9"] = (dftest["Amount_N_2"] >= 3)
dftest["inv_page_pred_9"] = (dftest["inv_page_pred_9"] == 1) | ((dftest["Label_N"] >= 10) & (dftest["Date_N"] != 0))
#dftest["inv_page_pred_9"] = (dftest["inv_page_pred_9"] == 1) | (dftest["vlines"] != 0)
dftest["inv_page_pred_9"] = (dftest["inv_page_pred_9"] == 1) | ((dftest["Label_N_2"] > 0) & (dftest["Amount_N_2"] > 0) & (dftest["Amount_N_2"] < 3))

dftest["inv_page"] = df["Inv Page"]
dftest["Filename"] = df["FileName"]
dftest["Page"] = df["page #"]
dftest["Words"] = df["Total Words"]

TP = dftest[(dftest["inv_page_pred_1"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_1"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_1"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_1"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 1: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_1"] = TP
dftest["FP_1"] = FP
dftest["FN_1"] = FN
dftest["prec_1"] = precision
dftest["recall_1"] = recall

TP = dftest[(dftest["inv_page_pred_2"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_2"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_2"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_2"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 2: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_2"] = TP
dftest["FP_2"] = FP
dftest["FN_2"] = FN
dftest["prec_2"] = precision
dftest["recall_2"] = recall

TP = dftest[(dftest["inv_page_pred_3"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_3"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_3"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_3"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 3: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_3"] = TP
dftest["FP_3"] = FP
dftest["FN_3"] = FN
dftest["prec_3"] = precision
dftest["recall_3"] = recall

TP = dftest[(dftest["inv_page_pred_4"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_4"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_4"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_4"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 4: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_4"] = TP
dftest["FP_4"] = FP
dftest["FN_4"] = FN
dftest["prec_4"] = precision
dftest["recall_4"] = recall

TP = dftest[(dftest["inv_page_pred_5"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_5"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_5"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_5"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 5: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_5"] = TP
dftest["FP_5"] = FP
dftest["FN_5"] = FN
dftest["prec_5"] = precision
dftest["recall_5"] = recall

TP = dftest[(dftest["inv_page_pred_6"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_6"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_6"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_6"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 6: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_6"] = TP
dftest["FP_6"] = FP
dftest["FN_6"] = FN
dftest["prec_6"] = precision
dftest["recall_6"] = recall

TP = dftest[(dftest["inv_page_pred_7"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_7"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_7"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_7"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 7: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_7"] = TP
dftest["FP_7"] = FP
dftest["FN_7"] = FN
dftest["prec_7"] = precision
dftest["recall_7"] = recall

TP = dftest[(dftest["inv_page_pred_8"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_8"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_8"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_8"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 8: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_8"] = TP
dftest["FP_8"] = FP
dftest["FN_8"] = FN
dftest["prec_8"] = precision
dftest["recall_8"] = recall

TP = dftest[(dftest["inv_page_pred_9"] == 1) & (dftest["inv_page"] == 1)].shape[0]
FP = dftest[(dftest["inv_page_pred_9"] == 1) & (dftest["inv_page"] == 0)].shape[0]
TN = dftest[(dftest["inv_page_pred_9"] == 0) & (dftest["inv_page"] == 0)].shape[0]
FN = dftest[(dftest["inv_page_pred_9"] == 0) & (dftest["inv_page"] == 1)].shape[0]

precision = TP/(TP+FP)
recall = TP/(TP+FN)

print("Method 9: ", "TP: ",TP,"FP: ",FP,"TN: ",TN,"FN: ",FN,
      "Precision: ",precision,"Recall: ",recall)

dftest["TP_9"] = TP
dftest["FP_9"] = FP
dftest["FN_9"] = FN
dftest["prec_9"] = precision
dftest["recall_9"] = recall

dftest.to_excel("invpage_" + t + ".xlsx",index = False)

