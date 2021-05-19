import json
import pandas as pd
import os
import glob
import numpy as np
import re
#import time
from price_parser import parse_price
import spacy
import sqlite3
#import gensim.models.fasttext as fasttext
#import csv
import random
#import sys
import cv2
import datetime

random.seed(0)

import warnings
warnings.filterwarnings("ignore")

scr = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\ocrs\Shankar"
formatTracker = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\formatTracker.csv" # Change Value if don't Have split tracker

des = str(scr)+"_output"    # Modify if required in Specific output folder

ocrpath = os.path.join(scr,"ocrs")
labelpath = os.path.join(scr,"labels")
imagepath = os.path.join(scr,"images")
extnlabel = ".labels.json"

#############
isCSVRequired_OCR = True
isCSVRequired_Table = True
isCSVRequired_Label = True
isOCRLabelCombinedRequired_PerFile = True
isOCRLabelCombinedRequired_PerFolder = False
isFeatureExtractionRequired = True
isFeatureRequired_PerFile = True
isFeatureRequired_PerFolder = False
#############

if not os.path.exists(des):
    os.mkdir(des)

if os.path.exists(formatTracker):
    DF_format = pd.read_csv(formatTracker)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
nlp = spacy.load('en_core_web_sm', disable=["parser"])
nlp.add_pipe(nlp.create_pipe('sentencizer'))
cat_encoding = {'NER_Spacy': ['CARDINAL', 'DATE', 'GPE', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON',
                              'PRODUCT', 'QUANTITY', 'TIME', 'UKWN']}

neighbWords = ["W1Ab","W2Ab","W3Ab","W4Ab","W5Ab","d1Ab","d2Ab","d3Ab","d4Ab","d5Ab","W1Be","W2Be","W3Be","W4Be","W5Be","d1Be","d2Be","d3Be","d4Be","d5Be","W1Lf","W2Lf","W3Lf","W4Lf","W5Lf","d1Lf","d2Lf","d3Lf","d4Lf","d5Lf","W1Rg","W2Rg","W3Rg","W4Rg","W5Rg","d1Rg","d2Rg","d3Rg","d4Rg","d5Rg"]
neighbWordsVec = ["W1Ab","W2Ab","W3Ab","W4Ab","W5Ab","W1Be","W2Be","W3Be","W4Be","W5Be","W1Lf","W2Lf","W3Lf","W4Lf","W5Lf","W1Rg","W2Rg","W3Rg","W4Rg","W5Rg"]
noOfPuncs_list = ["noOfPuncs","countOfColon","countOfSemicolon","countOfHyphen","countOfComma","countOfPeriod"]
lineInfo = ["lineTop","topLineLen","lineDown","downLineLen","lineLeft","leftLineLen","lineRight","rightLineLen"]

labelKeywords = {'hdr_1_UOM': ['unit', 'uom'],
 'hdr_1_itemDescription': ['description',  'details',  'item',  'product',  'activity',  'service',  'services',  'material',  'name',  'number',  'invoice',  'particulars'],
 'hdr_1_itemQuantity': ['quantity', 'qty', 'shipped', 'units'],
 'hdr_1_itemValue': ['amount',  'total',  'net',  'value',  'price',  'amt',  'line',  'extended',  'gross',  'cost',  'vat'],
 'hdr_1_itemcode': ['item', 'code', 'product', 'number', 'part', 'job'],
 'hdr_1_serviceEndDate': ['date'],
 'hdr_1_serviceStartDate': ['date', 'period', 'start'],
 'hdr_1_taxAmount': ['vat', 'amount', 'tax'],
 'hdr_1_taxRate': ['vat', 'rate', 'tax'],
 'hdr_1_unitPrice': ['price', 'unit', 'rate', 'net', 'cost'],
 'hdr_2_itemDescription': ['description'],
 'hdr_2_itemQuantity': ['qty'],
 'hdr_2_itemValue': ['total', 'amount'],
 'hdr_2_unitPrice': ['price', 'unit'],
 'lblAmountPaid': ['payments', 'credits'],
 'lblBillingAddress': ['invoice',  'bill',  'address',  'billing',  'client',  'customer',  'sold'],
 'lblCurrency': ['currency'],
 'lblCustomerAddress': ['invoice', 'address'],
 'lblCustomerId': ['customer',  'account',  'number',  'code',  'id',  'client',  'ref'],
 'lblCustomerName': ['customer', 'client', 'name'],
 'lblDiscountAmount': ['discount'],
 'lblDueDate': ['due', 'date', 'payment', 'invoice'],
 'lblEntityGSTIN': ['vat',  'number',  'reg',  'customer',  'client',  'id',  'registration',  'tax'],
 'lblFreightAmount': ['freight'],
 'lblInvoiceDate': ['date', 'invoice', 'tax', 'point'],
 'lblInvoiceNumber': ['invoice', 'number', 'document', 'credit', 'ref'],
 'lblInvoicedate': ['date', 'invoice', 'tax', 'point', 'issue'],
 'lblPaymentTerms': ['terms', 'payment', 'due'],
 'lblPoNumber': ['po',  'order',  'number',  'purchase',  'reference',  'ref',  'customer',  'client',  'cust'],
 'lblShippingAddress': ['ship', 'address', 'delivery', 'deliver', 'delivered'],
 'lblSubTotal': ['total',  'subtotal',  'net',  'sub',  'amount',  'vat',  'excl',  'value',  'invoice',  'goods',  'excluding',  'nett'],
 'lblTaxAmount': ['vat', 'total', 'tax', 'amount', 'sales'],
 'lblTotalAmount': ['total',  'invoice',  'due',  'amount',  'vat',  'balance',  'gross',  'grand',  'payable',  'incl',  'value',  'pay',  'including',  'final',  'net'],
 'lblVATRate': ['vat', 'rate', 'total', 'tax'],
 'lblVATTotal': ['vat', 'total', 'amount', 'tax'],
 'lblVendorAddress': ['address', 'registered', 'office'],
 'lblVendorEmail': ['email', 'mail', 'contact'],
 'lblVendorGSTIN': ['vat',  'number',  'reg',  'registration',  'id',  'tax',  'company',  'gst'],
 'isCurreny' : ["GBP","SGD","USD","EUR","EURO","pound","Pounds","Sterling","(GBP)","GBR","GB","Pounds.","KES","GBP-British","(EUR)","$","GBP:","ZAR","INR"],
 'isUOM' : ["db","DAY","Piece","EA","PCS","m","pc.","CYL","EACH","PC","LT","Pallets","Case","KG","Pallet","Lot","Hour","Lots","PCE","(EA)","PR","PRC","YR","unit","EUX","Units","User","License","STK","pes","PE","GFN","stk."],
 'isCountry' : ["Europe","England","UK","Columbus","US","Singapore","Hertfordshire","Stamford","Ireland","Milano","Devon","Oxon","Peruwelz","France","Nottingham","Canada","The Netherlands","South Glos","Gurugram","Manchester","Berkshire","Wereda","Peldanyszam","Draper","Buckinghamshire","Scotland","St Helens","New Yorl","London","East Sussex","Polaska","Myanmar","Japan","Middlesex","Ballygowan","Belgium","Boerne","Germany","Herts","Cambridge","United Kingdom","Esparreguera","Some rse t","Kent","India","Netherlands","Madrid","Amsterdam The Netherlands","South Africa","Alpharetta","Antrim","Nr Knutsford","Pretoria","Australia","Dalla","Italy","New York","United States of America","California","EDINBURGH","Great Britain","Brussels","Whybrow","Krakow","Uruguay","Leeds","New Bury","Washington","NSW","Brentford","Harlow","Switzerland","West Sussex","Hampshire","Surrey","Hong Kong","Middlesbrough","Glasgow","Cheshire","Essex","Koln","Twickenham","Warwick","Liverpool","Lancashire","Yorkshire","Sussex","Tamworth","Hamshipre","Westhoughton","Aldates","Britain","Brooklyn","Peebles","Darmstadt","Buckinghumshipre","Kulmbach","Estate York","Salford","Nertherland","Preston","Huntingdon","Warrington","Orlando","Berkshipre","Co.Louth","Pennsylvania","Bangkok","Runcorn","Stafforshipre","USA","Narthampton","Edingurgh","Wycombe","Penarth","Staffordshire","Swindon","Dublin","Netherland","BRISTOL","Dorset","Lincolnshipre","Brasil","Masku","Caerphilly","Aldershot","Wrexham","Birmingham","Durban","Slough","Pepper lane","Holywood","Denmark","Bolton","Shropshire","Albans","West Midlands","Hempstead","Cumbernauld","Kholin","West Yorkshire","Cheshipre","Derby","Kenya","Basingstoke","Northamptonshipre","Westfallca","Ethiopia","Korea","CA","Nevada","Chicago","Las vegas","NV","IND","AUS"],
 'isKeyword' : ['invoice','inv','quantity','qty','item','po','number','no.','description','desc','payment','terms','net','days','due','date','dt','reference','vat','tax','total','unit','units','price','amount','amt','bill','ship','billing','shipping','address','payment','reference','value','unit','purchase','ref','uom','weight','wt','services','service','fee','charge','charges','gst','rate','currency','order','discount','subtotal','sub-total','ship','balance','code','period','bank','remittance','account','advice','customer']
}

fileNo = 1
rows = []
featureRows = pd.DataFrame()

text_emb = []
rev_emb = []
shape_emb = []
EMBED_DIME = 30
for i in range(1,EMBED_DIME + 1):
    text_emb.append("emb_"+str(i))
    shape_emb.append("shape_"+str(i))
    rev_emb.append("rev_"+str(i))

foo = lambda x: pd.Series([i for i in x])
oof = lambda x: pd.Series([i for i in reversed(x)])

def isAlphaNumeric(text):
    return 1 if not(pd.isna(text)) and text.isalnum() else 0


def isAlpha(text):
    return 1 if not(pd.isna(text)) and str(text).isalpha() else 0


def isNumber(text):
    return 1 if  not(pd.isna(text)) and str(text).isdigit() else 0

def noOfPuncs(text):
    count = 0
    colon = 0
    semicolon = 0
    hyphen = 0
    comma = 0
    period = 0

    if not isNumber(text) and not type(text) == float:
        for i in range (0, len(str(text))):
            txt = text[i]
            if txt in ('!', "," ,"\'" ,";" ,"\"",":", ".", "-" ,"?"):  
                if txt == ':':
                    colon = colon + 1
                elif txt == ';':
                    semicolon = semicolon + 1
                elif txt == '-':
                    hyphen = hyphen + 1
                elif txt == ',':
                    comma = comma + 1
                elif txt == '.':
                    period = period + 1
                count = count + 1

    return [count,colon,semicolon,hyphen,comma,period]


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
        if len(l1) == 1:
            return 1
    except:
        return 0
    return 1


def w2v(key):
    missing = [0]*EMBED_DIME
    try:
        for i in range(len(str(key))):
            txt = str(key)[i]
            missing[i] = round(ord(txt) / 255, 5)
        return missing
    except:
        return missing

def wordshape(text):
    if not(pd.isna(text)):
        t1 = re.sub('[A-Z]', 'X',text)
        t2 = re.sub('[a-z]', 'x', t1)
        return re.sub('[0-9]', 'd', t2)
    return text

def reindex_by_page(leng, DF):
    DF_new = pd.DataFrame()
    tempar = pd.DataFrame()
    for i in range(1,leng+1):
        temp = DF['page_num'] == i
        tempar = DF[temp].copy()
        tempar["word_sequence"] = list(range(len(tempar)))
        DF_new = DF_new.append(tempar)
        
    return DF_new

def isID(row):
    if (not pd.isna(row['text'])) and row["len_digit"] > 0 and row["len_digit"] > row["len_alpha"] and len(str(row['text'])) > 7 and row["DATE"] == 0 and row["is_email"] == 0:
        list_id = 1
    else:
        list_id = 0
    
    return list_id

def isLabel(feature):
    for i in labelKeywords:
        feature[i] = [1 if t in labelKeywords[i] else 0 for t in [text for text in feature['text'].str.lower()] or 0]

    return feature

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

    pixelThresh = .05
    
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
                word1ab = j["text"]
                d1ab = round(j["top"] - row["top"],5)
            elif cnt == 1:
                word2ab = j["text"]
                d2ab = round(j["top"] - row["top"],5)
            elif cnt == 2:
                word3ab = j["text"]
                d3ab = round(j["top"] - row["top"],5)
            elif cnt == 3:
                word4ab = j["text"]
                d4ab = round(j["top"] - row["top"],5)
            elif cnt == 4:
                word5ab = j["text"]
                d5ab = round(j["top"] - row["top"],5)
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
                word1be = j["text"]
                d1be = round(j["top"] - row["top"],5)
            elif cnt == 1:
                word2be = j["text"]
                d2be = round(j["top"] - row["top"],5)
            elif cnt == 2:
                word3be = j["text"]
                d3be = round(j["top"] - row["top"],5)
            elif cnt == 3:
                word4be = j["text"]
                d4be = round(j["top"] - row["top"],5)
            elif cnt == 4:
                word5be = j["text"]
                d5be = round(j["top"] - row["top"],5)
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

    left = row["left"] - pixelThresh
    dffilt = df[(df["right"] >= left) & (df["right"] < row["left"])]
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [left,row["top"],row["right"],row["bottom"]]
        rect2 = [j["left"],j["top"],j["right"],j["bottom"]]
        overlap = isOverlap(rect1,rect2)
        if overlap:
            if cnt == 0:
                word1lf = j["text"]
                d1lf = round(j["left"] - row["left"],5)
            elif cnt == 1:
                word2lf = j["text"]
                d2lf = round(j["left"] - row["left"],5)
            elif cnt == 2:
                word3lf = j["text"]
                d3lf = round(j["left"] - row["left"],5)
            elif cnt == 3:
                word4lf = j["text"]
                d4lf = round(j["left"] - row["left"],5)
            elif cnt == 4:
                word5lf = j["text"]
                d5lf = round(j["left"] - row["left"],5)
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

    right = row["right"] + pixelThresh
    dffilt = df[(df["left"] <= right) & (df["left"] > row["right"])]
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [row["left"],row["top"],right,row["bottom"]]
        rect2 = [j["left"],j["top"],j["right"],j["bottom"]]
        overlap = isOverlap(rect1,rect2)
        if overlap:
            if cnt == 0:
                word1rg = j["text"]
                d1rg = round(j["left"] - row["left"],5)
            elif cnt == 1:
                word2rg = j["text"]
                d2rg = round(j["left"] - row["left"],5)
            elif cnt == 2:
                word3rg = j["text"]
                d3rg = round(j["left"] - row["left"],5)
            elif cnt == 3:
                word4rg = j["text"]
                d4rg = round(j["left"] - row["left"],5)
            elif cnt == 4:
                word5rg = j["text"]
                d5rg = round(j["left"] - row["left"],5)
            else:
                break
            cnt += 1

    return pd.Series([word1ab,word2ab,word3ab,word4ab,word5ab,d1ab,d2ab,d3ab,d4ab,d5ab,word1be,word2be,word3be,word4be,word5be,d1be,d2be,d3be,d4be,d5be,word1lf,word2lf,word3lf,word4lf,word5lf,d1lf,d2lf,d3lf,d4lf,d5lf,word1rg,word2rg,word3rg,word4rg,word5rg,d1rg,d2rg,d3rg,d4rg,d5rg])

def wordBoundingText(DF, leng):
    DF_new = pd.DataFrame()
    tempar = pd.DataFrame()

    for i in range(1,leng+1):
        temp = DF['page_num'] == i
        tempar = DF[temp].copy()
        tempar[neighbWords] = tempar.apply(findWordsClose,args=(tempar,),axis = 1)

        if DF_new.shape[0] == 0:
            DF_new = tempar
        else:
            DF_new = DF_new.append(tempar)

    return DF_new

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

def getLineInfo(DF, imagepath):
    DF_new = pd.DataFrame()
    tempar = pd.DataFrame()

    ret, imgs = cv2.imreadmulti(imagepath)

    for i, img in enumerate(imgs):

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

        temp = DF['page_num'] == i + 1
        tempar = DF[temp].copy()
        if tempar.shape[0] > 0:
            tempar[lineInfo] = tempar.apply(findLinesClose, args=(hlines,vlines),axis = 1)
            if DF_new.shape[0] == 0:
                DF_new = tempar
            else:
                DF_new = DF_new.append(tempar)

    return DF_new


def word_to_vector(DF):
    temp = []
    for ind in neighbWordsVec:
        for i in range(1,EMBED_DIME + 1):
            temp.append(str(ind)+"_"+str(i))

        DF['temp1'] = DF[ind].apply(w2v)
        DF[temp] = DF["temp1"].apply(foo)
        temp = []
        del DF['temp1']

    return DF


def readResultTag(resultList, formatNo):
    
    rows = []
    tokenid = 10000
    
    for resultobj in resultList:
        pageNo = resultobj["page"]
        lines = resultobj["lines"]
        width = resultobj["width"]
        height = resultobj["height"]
        lineNo = 0
        for line in lines:
            value = line["text"]
            bb = line["boundingBox"]
            left = min(bb[0], bb[6]) / width
            right = max(bb[2], bb[4]) / width
            top = min(bb[1],bb[3]) / height
            down = max(bb[5],bb[7]) / height
            # print(pageNo,lineNo,value,left,right,top,down)
            
            words = line["words"]
            wordNo = 0
            for word in words:
                row = {}
                wordValue = word["text"]
                wordConfidence = word["confidence"]
                wordBB = word["boundingBox"]
                wordLeft = min(wordBB[0], wordBB[6]) / width
                wordRight = max(wordBB[2], wordBB[4]) / width
                wordTop = min(wordBB[1],wordBB[3]) / height
                wordDown = max(wordBB[5],wordBB[7]) / height
                row["File#"] = fileNo
                row["Filename"] = filename[:-9] 
                row["format"] = formatNo
                row["tokenid"] = tokenid    
                row["tagger"] = tagger
                row["page_num"] = pageNo
                row["line_num"] = lineNo
                row["line_text"] = value
                row["line_left"] = round(left,3)
                row["line_top"] = round(top,3)
                row["line_height"] = round(down - top,3)
                row["line_width"] = round(right - left,3)
                row["line_right"] = round(right,3)
                row["line_down"] = round(down,3)
                row["word_num"] = wordNo
                row["word_text"] = wordValue
                row["conf"] = wordConfidence
                row["word_left"] = round(wordLeft,3)
                row["word_top"] = round(wordTop,3)
                row["word_height"] = round(wordDown - wordTop,3)
                row["word_width"] = round(wordRight - wordLeft,3)
                row["word_right"] = round(wordRight,3)
                row["word_down"] = round(wordDown,3)
                row["image_height"] = height
                row["image_widht"] = width
                rows.append(row)

                wordNo = wordNo + 1
                tokenid = tokenid + 1
            lineNo = lineNo + 1
            
    return rows


def GetElementText(word,result,width,height,row):
    pageCount=word.split("readResults/")[1]
    lineCount=pageCount.split("/")[2]
    wordCount=pageCount.split("/")[-1]
    pageNo=pageCount.split("/lines")[0]
    Text=result[int(pageNo)]["lines"][int(lineCount)]["words"][int(wordCount)]["text"]
    bb=result[int(pageNo)]["lines"][int(lineCount)]["words"][int(wordCount)]["boundingBox"]   
    #print(bb)    
    left = min(bb[0], bb[6]) / width
    right = max(bb[2], bb[4]) / width
    top = min(bb[1],bb[3]) / height
    down = max(bb[5],bb[7]) / height
    row['Text'] = Text
    row["left"] = round(left,3)
    row["top"] = round(top,3)
    row["right"] = round(right,3)
    row["down"] = round(down,3)
    
    return row


def readPageResult(pageList, resultList):
    
    rows = []

    for i in range(0, len(resultList)):
        width = resultList[i]["width"]
        height = resultList[i]["height"]
        tables = pageList[i]['tables']
        pageNo = pageList[i]['page']
        tableID=1
        for t in tables:
            for cel in t["cells"]:
                rowIndex=cel["rowIndex"]
                colIndex=cel["columnIndex"]
                WordCount=cel["elements"]
                for word in WordCount:
                    row = {}
                    row["pageNo"] = pageNo
                    row["filename"] = orginalName
                    row["tableID"] = tableID
                    row["rowNo"] = rowIndex+1
                    row["ColNo"] = colIndex+1
                    row = GetElementText(word,resultList,width,height,row)
                    rows.append(row)
            tableID=tableID+1

    return rows


def joinTableInfo(df_1,df_2):
    df_1["tableNo"] = ""
    df_1["rowNo"] = ""
    df_1["colNo"] = ""

    for index, row in df_2.iterrows():
        word = row["Text"]
        left = row["left"]
        right = row["right"]
        top = row["top"]
        down = row["down"]

        hasMatch = df_1.loc[(df_1["word_text"] == word) & (df_1["word_left"] == left) & (df_1["word_right"] == right) & (df_1["word_top"] == top) & (df_1["word_down"] == down), ["tableNo","rowNo","colNo"]] = [row['tableID'],row['rowNo'],row['ColNo']]

    return df_1

def readOCR(path):

    formatNo = ""

    if os.path.exists(formatTracker): # to get Format #
        Filename = filename[:-9]
        has = DF_format.loc[DF_format['Filename']==Filename, "Format"]
        if len(has) > 0:
            formatNo = has.values[0]

    f = open(path,"r")
    o = f.read()
    f.close()
    j = json.loads(o)
    resultList = j["analyzeResult"]["readResults"]
    pageList = j["analyzeResult"]["pageResults"]
    rows = readResultTag(resultList, formatNo)
    rows_1 = readPageResult(pageList, resultList)
    
    df_1 = pd.DataFrame(rows)
    df_2 = pd.DataFrame(rows_1)
    
    df = joinTableInfo(df_1,df_2)
    
    csvoutpath = os.path.join(des,"ocrs",tagger)
    if isCSVRequired_OCR:
        if not os.path.exists(csvoutpath):
            os.makedirs(csvoutpath)
        df.to_csv(os.path.join(csvoutpath,orginalName+".csv"),index = False)

    if isCSVRequired_Table:
        
        csvTablePath = os.path.join(csvoutpath,"Table")
        if not os.path.exists(csvTablePath):
            os.makedirs(csvTablePath)

        df_2.to_csv(os.path.join(csvTablePath,orginalName+".csv"),index = False)     

    return df


def readlabel(path):

    rows = []
    f = open(path,"r")
    o = f.read()
    f.close()
    j = json.loads(o)
    labellist = j["labels"]
    for labelobj in labellist:
        
        labelname = labelobj["label"]
        values = labelobj["value"]
        for val in values:
            row = {}
            value = val["text"]
            bb = val["boundingBoxes"][0]
            left = min(bb[0], bb[6])
            right = max(bb[2], bb[4])
            top = min(bb[1],bb[3])
            down = max(bb[5],bb[7])
            page = val["page"]
            row["File#"] = fileNo
            row["filename"] = orginalName
            row["taggername"] = tagger
            row["page"] = page
            row["label"] = labelname
            row["value"] = value
            row["left"] = round(left,3)
            row["top"] = round(top,3)
            row["right"] = round(right,3)
            row["down"] = round(down,3)
            row["height"] = round(down - top,3)
            row["width"] = round(right - left,3)
            rows.append(row)
                        
    df = pd.DataFrame(rows)

    if isCSVRequired_Label:
        csvoutpath = os.path.join(des,"labels",tagger)
        if not os.path.exists(csvoutpath):
            os.makedirs(csvoutpath)

        df.to_csv(os.path.join(csvoutpath,orginalName+".csv"),index = False)

    return df


def findLabel(label,ocr):
    finalrows = []

    # print(label,ocr)
    for index, row in ocr.iterrows():

        finalrow = {}
        filename = row["Filename"]
        text = row["word_text"]
        left = row["word_left"]
        right = row["word_right"]
        top = row["word_top"]
        down = row["word_down"]

        if type(label) != str:
            hasMatch = label.loc[(label["filename"] == filename) & (label["left"] == left) & (label["right"] == right) & (label["top"] == top) & (label["down"] == down), "label"]
            # print(hasMatch)
            if len(hasMatch) == 1:
                status = hasMatch.values[0]
            else:
                status = "Unknown"
        else:
            status = "Unknown"

        finalrow["token_id"] = row["tokenid"]
        finalrow["level"] = 0
        finalrow["page_num"] = row["page_num"]
        finalrow["block_num"] = 0
        finalrow["par_num"] = 0
        finalrow["line_num"] = row["line_num"]
        finalrow["word_num"] = row["word_num"]
        finalrow["left"] = row["word_left"]
        finalrow["top"] = row["word_top"]
        finalrow["width"] = row["word_width"]
        finalrow["height"] = row["word_height"]
        finalrow["conf"] = row["conf"]
        finalrow["text"] = row["word_text"]
        finalrow["right"] = row["word_right"]
        finalrow["bottom"] = row["word_down"]
        finalrow["label"] = status
        finalrow["Folder"] = row["format"]
        finalrow["OriginalFile"] = row["Filename"]
        finalrow["SplitFile"] = row["Filename"].split(".")[0] + "_" + str(row["page_num"]) + "." + row["Filename"].split(".")[1]
        finalrow["region_id"] = 999
        finalrow["region_left"] = 0
        finalrow["region_right"] = 0
        finalrow["region_top"] = 0
        finalrow["region_bottom"] = 0
        finalrow["image_height"] = row["image_height"]
        finalrow["image_width"] = row["image_widht"]
        finalrow["tableNo"] = row["tableNo"]
        finalrow["rowNo"] = row["rowNo"]
        finalrow["colNo"] = row["colNo"]

        finalrows.append(finalrow)

    return finalrows


def find_left_right_text(DF, offset, left_right):
    """
    Method finds left and right text
    :param DF:
    :param offset:
    :param left_right:
    :return:
    """
    col_name = ""
    col_name_margin = ""
    if abs(offset) == 1:
        col_name = left_right + "_text"
        col_name_margin = left_right + "_text_margin"
    if abs(offset) == 2:
        col_name = "second_" + left_right + "_text"
        col_name_margin = "second_" + left_right + "_text_margin"

    # Find left text
    temp = DF.copy()
    temp['word_num'] = temp['word_num'] + offset

    AA = pd.merge(DF, temp[['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num', 'text',
                            'left', 'right', 'top', 'bottom']],
                  on=['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num'],
                  how='left')

    AA = AA.rename(columns={'text_x': 'text', 'text_y': col_name})

    if left_right == 'left':
        AA[col_name_margin] = AA['left_x'] - AA['right_y']
    if left_right == 'right':
        AA[col_name_margin] = AA['left_y'] - AA['right_x']

    DF[col_name] = None
    DF[col_name_margin] = 10000

    DF.loc[list(AA['index']), col_name] = list(AA[col_name])
    DF.loc[list(AA['index']), col_name_margin] = list(AA[col_name_margin])

    DF[col_name].fillna("NONE", inplace=True)
    DF[col_name_margin].fillna(10000, inplace=True)


def find_top_text(DF):
    """
    Method finds top and surrounding top texts
    :param DF:
    :return:
    """
    temp = DF.copy()
    # Make the db in memory
    conn = sqlite3.connect(':memory:')
    # write the tables
    temp.to_sql('temp', conn, index=False)
    DF.to_sql('DF', conn, index=False)

    qry = '''
    select  
        temp.OriginalFile AS OriginalFile,
        temp.SplitFile AS SplitFile,
        temp.block_num AS block_num,
        temp.par_num AS par_num,
        temp.line_num AS line_num,
        temp.word_num AS word_num,

        temp.[index] AS index_new,
        temp.text AS text_new,
        temp.left AS left_new,
        temp.right as right_new,
        temp.top AS top_new,
        temp.bottom AS bottom_new,

        DF.text AS text_original,
        DF.top AS top,
        DF.bottom AS bottom,
        DF.[index] AS index_original
    FROM DF
        JOIN temp on
        temp.OriginalFile = DF.OriginalFile AND
        temp.SplitFile = DF.SplitFile AND
        (temp.bottom < DF.top AND
        (((temp.left >= DF.left) AND (temp.left <= DF.right)) OR 
         ((temp.right >= DF.left) AND (temp.right <= DF.right)) OR
         ((temp.left <= DF.left) AND (temp.right >= DF.right))))
         ORDER BY temp.top DESC, temp.left ASC
    '''

    AA = pd.read_sql_query(qry, conn)

    BB = AA.groupby('index_original').first().reset_index()
    BB = BB.rename(columns={'text_new': 'top_text'})
    BB['top_text_margin'] = BB['top'] - BB['bottom_new']

    DF['top_text'] = None
    DF['top_text_margin'] = 10000

    DF.loc[list(BB['index_original']), 'top_text'] = list(BB['top_text'])
    DF.loc[list(BB['index_original']), 'top_text_margin'] = list(BB['top_text_margin'])

    # Find left top word
    # Taking BB as reference
    temp = BB.copy()
    temp['word_num'] = temp['word_num'] - 1
    AA = pd.merge(temp,
                  DF[['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num', 'text', 'top', 'bottom',
                      'left', 'right']],
                  on=['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num'],
                  how='left')

    AA = AA.rename(columns={'text': 'left_top_text'})
    AA['left_top_text_left_margin'] = AA['right']

    AA = AA[['index_original', 'left_top_text', 'left_top_text_left_margin']].drop_duplicates()

    DF['left_top_text'] = None
    DF['left_top_text_left_margin'] = None

    DF.loc[list(AA['index_original']), 'left_top_text'] = list(AA['left_top_text'])
    DF.loc[list(AA['index_original']), 'left_top_text_left_margin'] = list(AA['left_top_text_left_margin'])
    DF['left_top_text_left_margin'] = DF['left'] - DF['left_top_text_left_margin']

    DF['left_top_text_left_margin'].fillna(10000, inplace=True)

    # Find right top word
    # Taking BB as reference
    temp = BB.copy()
    temp['word_num'] = temp['word_num'] + 1
    AA = pd.merge(temp,
                  DF[['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num', 'text', 'top', 'bottom',
                      'left', 'right']],
                  on=['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num'],
                  how='left')

    AA = AA.rename(columns={'text': 'right_top_text'})
    AA['right_top_text_right_margin'] = AA['left']

    AA = AA[['index_original', 'right_top_text', 'right_top_text_right_margin']].drop_duplicates()

    DF['right_top_text'] = None
    DF['right_top_text_right_margin'] = None

    DF.loc[list(AA['index_original']), 'right_top_text'] = list(AA['right_top_text'])
    DF.loc[list(AA['index_original']), 'right_top_text_right_margin'] = list(AA['right_top_text_right_margin'])
    DF['right_top_text_right_margin'] = DF['right_top_text_right_margin'] - DF['right']

    DF['right_top_text_right_margin'].fillna(10000, inplace=True)


def find_bottom_text(DF):
    """
    Method finds bottom and surrounding bottom texts
    :param DF: Input DataFrame
    :return:
    """
    temp = DF.copy()
    #Make the db in memory
    conn = sqlite3.connect(':memory:')
    #write the tables
    temp.to_sql('temp', conn, index=False)
    DF.to_sql('DF', conn, index=False)
    # Find bottom text
    qry = '''
        select  
            temp.OriginalFile AS OriginalFile,
            temp.SplitFile AS SplitFile,
            temp.block_num AS block_num,
            temp.par_num AS par_num,
            temp.line_num AS line_num,
            temp.word_num AS word_num,

            temp.[index] AS index_new,
            temp.text AS text_new,
            temp.left AS left_new,
            temp.right as right_new,
            temp.top AS top_new,
            temp.bottom AS bottom_new,

            DF.text AS text_original,
            DF.top AS top,
            DF.bottom AS bottom,
            DF.[index] AS index_original
        FROM DF
            JOIN temp on
            temp.OriginalFile = DF.OriginalFile AND
            temp.SplitFile = DF.SplitFile AND
            (temp.top > DF.bottom AND
            (((temp.left >= DF.left) AND (temp.left <= DF.right)) OR 
             ((temp.right >= DF.left) AND (temp.right <= DF.right)) OR
             ((temp.left <= DF.left) AND (temp.right >= DF.right))))
             ORDER BY temp.top ASC, temp.left ASC
        '''

    AA = pd.read_sql_query(qry, conn)

    BB = AA.groupby('index_original').first().reset_index()
    BB = BB.rename(columns={'text_new': 'bottom_text'})
    BB['bottom_text_margin'] = BB['top_new'] - BB['bottom']

    DF['bottom_text'] = None
    DF['bottom_text_margin'] = 10000

    DF.loc[list(BB['index_original']), 'bottom_text'] = list(BB['bottom_text'])
    DF.loc[list(BB['index_original']), 'bottom_text_margin'] = list(BB['bottom_text_margin'])


    # Find left bottom word
    # Taking BB as reference
    temp = BB.copy()
    temp['word_num'] = temp['word_num'] -  1
    AA = pd.merge(temp,
                  DF[['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num', 'text', 'top', 'bottom',
                'left', 'right']],
             on=['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num'],
             how='left')

    AA = AA.rename(columns={'text': 'left_bottom_text'})
    AA['left_bottom_text_left_margin'] = AA['right']

    AA = AA[['index_original', 'left_bottom_text', 'left_bottom_text_left_margin']].drop_duplicates()

    DF['left_bottom_text'] = None
    DF['left_bottom_text_left_margin'] = None

    DF.loc[list(AA['index_original']), 'left_bottom_text'] = list(AA['left_bottom_text'])
    DF.loc[list(AA['index_original']), 'left_bottom_text_left_margin'] = list(AA['left_bottom_text_left_margin'])
    DF['left_bottom_text_left_margin'] = DF['left'] - DF['left_bottom_text_left_margin']

    DF['left_bottom_text_left_margin'].fillna(10000, inplace=True)

    # Find right bottom word
    # Taking BB as reference
    temp = BB.copy()
    temp['word_num'] = temp['word_num'] +  1
    AA = pd.merge(temp,
                  DF[['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num', 'text', 'top',
                      'bottom', 'left', 'right']],
             on=['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num', 'word_num'],
             how='left')

    AA = AA.rename(columns={'text': 'right_bottom_text'})
    AA['right_bottom_text_right_margin'] = AA['left']

    AA = AA[['index_original', 'right_bottom_text', 'right_bottom_text_right_margin']].drop_duplicates()

    DF['right_bottom_text'] = None
    DF['right_bottom_text_right_margin'] = None

    DF.loc[list(AA['index_original']), 'right_bottom_text'] = list(AA['right_bottom_text'])
    DF.loc[list(AA['index_original']), 'right_bottom_text_right_margin'] = list(AA['right_bottom_text_right_margin'])
    DF['right_bottom_text_right_margin'] = DF['right_bottom_text_right_margin'] - DF['right']

    DF['right_bottom_text_right_margin'].fillna(10000, inplace=True)


def extract_text_features_(DF):
    DF.reset_index(inplace=True)
    find_left_right_text(DF, 1, "left")
    find_left_right_text(DF, 2, "left")
    find_left_right_text(DF, -1, "right")
    find_left_right_text(DF, -2, "right")
    find_top_text(DF)
    find_bottom_text(DF)
    del DF['index']


def extract_number_words_(df):
    """
    Extracts features related to number of words in the line
    :param df:
    :return:
    """
    temp = df.groupby(["OriginalFile", "SplitFile", "block_num", "par_num", "line_num"])[['text']].count().reset_index()
    temp = temp.rename(columns={'text': 'words_on_line'})

    df = pd.merge(df, temp, on=['OriginalFile', 'SplitFile', 'block_num', 'par_num', 'line_num'], how='left')
    return df


def extract_token_specific_features(df):
    """
    Extract specific token related features
    :param df:
    :return:
    """
    is_date = []
    is_number = []
    has_currency = []
    extracted_amount = []
    total_len_text = []
    len_digit = []
    len_alpha = []
    len_spaces = []

    for index, row in df.iterrows():
        text = row['text']
        try:
            pd.to_datetime(text)
            is_date.append(1)
        except:
            is_date.append(0)
            pass
        try:
            float(text.replace(',', ''))
            is_number.append(1)
        except:
            is_number.append(0)
            pass
        try:
            price = parse_price(text)
            if (not price.amount is None) and (not price.currency is None):
                extracted_amount.append(price.amount)
                has_currency.append(1)
            else:
                extracted_amount.append(None)
                has_currency.append(0)
        except:
            extracted_amount.append(None)
            has_currency.append(0)
            pass
        try:
            total_len_text.append(len(text))
            len_digit.append(sum(c.isdigit() for c in text))
            len_alpha.append(sum(c.isalpha() for c in text))
            len_spaces.append(sum(c.isspace() for c in text))
        except:
            total_len_text.append(0)
            len_digit.append(0)
            len_alpha.append(0)
            len_spaces.append(0)
            pass

    df['is_date'] = is_date
    df['is_number'] = is_number
    df['has_currency'] = has_currency
    df['extracted_amount'] = extracted_amount
    df['total_len_text'] = total_len_text
    df['len_digit'] = len_digit
    df['len_alpha'] = len_alpha
    df['len_spaces'] = len_spaces
    df['len_others'] = df['total_len_text'] - df['len_digit'] - df['len_alpha'] - df['len_spaces']


def extract_ner_spacy(df):
    """
    Extract Named Entity Recognition from Spacy
    :param df:
    :return:
    """
    df['NER_Spacy'] = "UKWN"

    for index, row in df.iterrows():
        text = str(row['text']).lower()
        doc = nlp(text)
        try:
            for ent in doc.ents:
                label = ent.label_
                df.at[index, 'NER_Spacy'] = label
                break
        except:
            pass


def check_email(s):
    """
    Check valid email
    :param s:
    :return:
    """
    if not EMAIL_REGEX.match(str(s)):
        return 0
    else:
        return 1


def extract_is_email(df):
    """
    Extract whether text is in email format or not
    :param df:
    :return:
    """
    df['is_email'] = df['text'].apply(check_email)


def scale_margin_attributes(df):
    """
    Scale Margin attributes
    :param df:
    :param page_height: Height of Page
    :param page_width: Width of Page
    :return:
    """
    height_cols = ['height', 'top_text_margin', 'bottom_text_margin', 'top', 'bottom']
    width_cols = ['width', 'left_text_margin', 'right_text_margin', 'second_left_text_margin',
                  'second_right_text_margin',
                  'left_top_text_left_margin', 'right_top_text_right_margin',
                  'left_bottom_text_left_margin', 'right_bottom_text_right_margin',
                  'left', 'right']
    for h in height_cols:
        df[h] = df[h] / df['image_height']

    for w in width_cols:
        df[w] = df[w] / df['image_width']

    for h in height_cols:
        df.loc[df[h] > 1.0, h] = 1.0

    for w in width_cols:
        df.loc[df[w] > 1.0, w] = 1.0


def extract_model_features(df):
    """
    Extract and build model features
    :param df:
    :return:
    """
    model_features = [  # Position of token
        'top', 'bottom', 'left', 'right',
        # Document Related features
        'document_page_number', 'page_num', 'level', 'block_num', 'par_num', 'line_num', 'word_num',
        'words_on_line',
        # Token related features
        'total_len_text', 'len_alpha', 'len_digit', 'len_spaces',
        # Spatial features related to surrounding tokens
        'top_text_margin', 'bottom_text_margin', 'left_text_margin', 'right_text_margin',
        'second_left_text_margin', 'second_right_text_margin',
        'right_bottom_text_right_margin', 'right_top_text_right_margin',
        'left_bottom_text_left_margin', 'left_top_text_left_margin',
        # Boolean features
        'is_date', 'has_currency', 'is_number', 'is_email',
        # Overall page height and width
        'page_height', 'page_width',
        # OCR confidence
        'conf',
        # NER features
        'NER_Spacy']

    cols_for_word2vec = ['text', 'left_text', 'right_text', 'second_left_text', 'second_right_text', 'top_text',
                         'bottom_text', 'left_top_text', 'right_top_text', 'left_bottom_text', 'right_bottom_text']
    l = list(range(1, 301))

    list_col_names_w2v = []
    for c in cols_for_word2vec:
        list_col_names_w2v.extend([str(c) + "_" + str(s) for s in l])

    # Convert boolean features to 0,1
    boolean_features = ['is_date', 'has_currency', 'is_number', 'is_email']
    for b in boolean_features:
        df[b] = df[b].fillna(0)
        df[b] = df[b].astype(int)

    # Get one-hot encoding for categorical features
    # NER_Spacy
    col_name = 'NER_Spacy'
    one_hot = pd.get_dummies(df[col_name])
    df = df.drop(col_name, axis=1)

    for c in cat_encoding[col_name]:
        df[c] = 0
    df[one_hot.columns] = one_hot

    model_features.remove(col_name)
    model_features.extend(cat_encoding[col_name])

    model_features.extend(list_col_names_w2v)

    # df.drop(columns = list(set(list(df.columns)) - set(model_features)), axis = 1, inplace = True)
    return df, model_features


def process_df_for_feature_extraction(df):

    
    df = df.loc[df['conf'] != '-1']
    df = df.reset_index(drop=True)
    df['conf'] = df['conf'].astype(float)
    extract_text_features_(df)
    df = extract_number_words_(df)
    extract_token_specific_features(df)
    extract_ner_spacy(df)
    extract_is_email(df)
    
    # scale_margin_attributes(df)   
    
    df, model_features = extract_model_features(df)
    
    ### Recently added
    df["isAlphaNumeric"] = df['text'].apply(isAlphaNumeric)
    df["isAlpha"] = df['text'].apply(isAlpha)
    df["isAmount"] = df['text'].apply(isAmount)
    df["wordshape"] = df['text'].apply(wordshape)
    df["noOfPuncs_list"] = df['text'].apply(noOfPuncs)
    df[noOfPuncs_list] = df["noOfPuncs_list"].apply(foo)
    df["isID"] = df.apply(isID, axis=1)

    
    df['vector'] = df['text'].apply(w2v)
    df[text_emb] = df["vector"].apply(foo)
    df[rev_emb] = df["vector"].apply(oof)

    df['vector'] = df['wordshape'].apply(w2v)
    df[shape_emb] = df["vector"].apply(foo)

    del df['vector']
    del df['wordshape']
    del df["noOfPuncs_list"]

    
    
    df = isLabel(df)
    
    df.sort_values(by=['page_num','top','left'], inplace=True)
    df = reindex_by_page(len(df["page_num"].unique()),df)
    
    df = wordBoundingText(df, len(df["page_num"].unique()))
    
    df = word_to_vector(df)
    df.drop(neighbWordsVec, axis = 1, inplace= True) # Drop if required
    
    name = glob.glob(os.path.join(str(imagepath),"*",orginalName))
    name = glob.glob(os.path.join(str(imagepath),orginalName))
    if len(name) > 0:
        imageFilepath = name[0]
        df = getLineInfo(df, imageFilepath)
    else:
        print("No Image File found for ",orginalName)
        # temp = {}
        # for i in lineInfo:
        #     temps = []
        #     for j in range(len(df)):
        #         temps.append("")
        #     temp[i] = temps

        # df[lineInfo] = temp
        # df = df.assign(lineInfo = temp)

    
    df.sort_values(by=['page_num','line_num','word_num'], inplace=True)

    
    if isFeatureRequired_PerFile:
        if not os.path.exists(os.path.join(des,"features",tagger)):
            os.makedirs(os.path.join(des,"features",tagger))
        df.to_csv(os.path.join(des,"features",tagger, orginalName.split(".")[0] +"_Features.csv"),index = False)

    return df


for root, subfolder, files in os.walk(ocrpath):
    # userRow = []
    # folder_df = pd.DataFrame()

    if len(files) > 0:

        tagger = os.path.split(root)[-1]

        for filename in files:
            try:
                if filename[-9:].upper() == ".OCR.JSON":
                    eachFile = []
                    orginalName = filename[:-9]
                    print(datetime.datetime.now(), fileNo, tagger ,orginalName)
                    ocrFilePath = os.path.join(root,filename)
                    name = glob.glob(os.path.join(str(labelpath),"*" ,orginalName+extnlabel))
                    name = glob.glob(os.path.join(str(labelpath),orginalName+extnlabel))
                    if len(name) > 0:
                        labelFilePath = name[0]
                    else:
                        labelFilePath = "-"
                        print("Labeled File is not found for :- "+orginalName)

                    # tagger = os.path.split(os.path.dirname(labelFilePath))[-1]
                    df_OCR = readOCR(ocrFilePath)
                    
                    if labelFilePath != "-" :
                        df_Label = readlabel(labelFilePath)
                        # print("\tEnd readlabel",datetime.datetime.now())
                    else:
                        df_Label = "-"
                    row = []
                    row = findLabel(df_Label,df_OCR)
                    for r in row:
                        # rows.append(r)
                        # userRow.append(r)
                        eachFile.append(r)

                    ### Feature Extraction
                    if isFeatureExtractionRequired:
                        temp_feature_df = process_df_for_feature_extraction(pd.DataFrame(eachFile))
                        # folder_df = folder_df.append(temp_feature_df)
                        # featureRows = featureRows.append(temp_feature_df)


                    if isOCRLabelCombinedRequired_PerFile:
                        if not os.path.exists(os.path.join(des,"analysis",tagger)):
                            os.makedirs(os.path.join(des,"analysis",tagger))
                        df_file = pd.DataFrame(eachFile)
                        df_file.to_csv(os.path.join(des, "analysis",tagger, orginalName.split(".")[0] +".csv"),index = False)

                    fileNo = fileNo + 1
            except Exception as e:
                print(fileNo," Exception Occured:- ", e)
                # df_user = pd.DataFrame(userRow)
                # df_user.to_csv(os.path.join(des, tagger +"_exc.csv"),index = False)
        
        if isOCRLabelCombinedRequired_PerFolder:
            df_user = pd.DataFrame(userRow)
            df_user.to_csv(os.path.join(des, tagger +"_Analysis.csv"),index = False)
        if isFeatureRequired_PerFolder:
            folder_df.to_csv(os.path.join(des, tagger +"_Features.csv"),index = False)

# df = pd.DataFrame(rows)
# df.to_csv(os.path.join(des,"Analysis_Combined.csv"),index = False)
# if isFeatureExtractionRequired :
#     featureRows.to_csv(os.path.join(des,"Features_Combined.csv"),index = False)
