#!/usr/bin/env python
# coding: utf-8

# In[1]:


from azure.storage.blob import BlobServiceClient
import json
import pandas as pd
import os
import glob
import numpy as np
import re
import time
from price_parser import parse_price
import spacy
import sqlite3
import csv
import random
import sys
import cv2
import datetime
import sys

random.seed(0)

import warnings
warnings.filterwarnings("ignore")

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
# print(connect_str)
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container = "tapp-data"
container_client = blob_service_client.get_container_client(container)
img_folder = 'DATASET_INVOICE_PAGES'
csv_folder = "DATASET_INVOICE_PAGES_OT_PHASE1_CSV"
out_feature_folder = "DATASET_INVOICE_PAGES_OT_PHASE1_FEATURE_1"


workingDirectory = 'Temp_Processing'
localWorkingDirectory = os.path.join(os.getcwd(),workingDirectory)
os.makedirs(localWorkingDirectory, exist_ok=True)


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
nlp = spacy.load('en_core_web_sm', disable=["parser"])
nlp.add_pipe(nlp.create_pipe('sentencizer'))
cat_encoding = {'NER_Spacy': ['CARDINAL', 'DATE', 'GPE', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON',
                              'PRODUCT', 'QUANTITY', 'TIME', 'UKWN']}

neighbWordsVec = ["W1Ab","W2Ab","W3Ab","W4Ab","W5Ab","W1Be","W2Be","W3Be","W4Be","W5Be","W1Lf","W2Lf","W3Lf","W4Lf","W5Lf","W1Rg","W2Rg","W3Rg","W4Rg","W5Rg"]
neighbWords = ["W1Ab","W2Ab","W3Ab","W4Ab","W5Ab","d1Ab","d2Ab","d3Ab","d4Ab","d5Ab","W1Be","W2Be","W3Be","W4Be","W5Be","d1Be","d2Be","d3Be","d4Be","d5Be","W1Lf","W2Lf","W3Lf","W4Lf","W5Lf","d1Lf","d2Lf","d3Lf","d4Lf","d5Lf","W1Rg","W2Rg","W3Rg","W4Rg","W5Rg","d1Rg","d2Rg","d3Rg","d4Rg","d5Rg"]
noOfPuncs_list = ["no_of_punctuation","no_of_colon","no_of_semicolon","no_of_hyphen","no_of_comma","no_of_period"]
lineInfo = ["lineTop","topLineLen","lineDown","downLineLen","lineLeft","leftLineLen","lineRight","rightLineLen"]

labelKeywords = {"hdr_UOM":["unit","uom"],"hdr_itemDescription":["description","details","item","product","activity","service","services","material","name","number","invoice","particulars"],"hdr_itemQuantity":["quantity","qty","shipped","units"],"hdr_itemValue":["amount","total","net","value","price","amt","line","extended","gross","cost","vat"],"hdr_itemcode":["item","code","product","number","part","job"],"hdr_serviceEndDate":["date"],"hdr_serviceStartDate":["date","period","start"],"hdr_taxAmount":["vat","amount","tax"],"hdr_taxRate":["vat","rate","tax"],"hdr_unitPrice":["price","unit","rate","net","cost"],"lblAmountPaid":["payments","credits"],"lblBillingAddress":["invoice","bill","address","billing","client","customer","sold"],"lblCurrency":["currency"],"lblCustomerAddress":["invoice","address"],"lblCustomerId":["customer","account","number","code","id","client","ref"],"lblCustomerName":["customer","client","name"],"lblDiscountAmount":["discount"],"lblDueDate":["due","date","payment","invoice"],"lblEntityGSTIN":["vat","number","reg","customer","client","id","registration","tax"],"lblFreightAmount":["freight"],"lblInvoiceDate":["date","invoice","tax","point"],"lblInvoiceNumber":["invoice","number","document","credit","ref"],"lblInvoicedate":["date","invoice","tax","point","issue"],"lblPaymentTerms":["terms","payment","due"],"lblPoNumber":["po","order","number","purchase","reference","ref","customer","client","cust"],"lblShippingAddress":["ship","address","delivery","deliver","delivered"],"lblSubTotal":["total","subtotal","net","sub","amount","vat","excl","value","invoice","goods","excluding","nett"],"lblTaxAmount":["vat","total","tax","amount","sales"],"lblTotalAmount":["total","invoice","due","amount","vat","balance","gross","grand","payable","incl","value","pay","including","final","net"],"lblVATRate":["vat","rate","total","tax"],"lblVATTotal":["vat","total","amount","tax"],"lblVendorAddress":["address","registered","office"],"lblVendorEmail":["email","mail","contact"],"lblVendorGSTIN":["vat","number","reg","registration","id","tax","company","gst"],"isCurreny":["GBP","SGD","USD","EUR","EURO","pound","Pounds","Sterling","(GBP)","GBR","GB","Pounds.","KES","GBP-British","(EUR)","$","GBP:","ZAR","INR"],"isUOM":["db","DAY","Piece","EA","PCS","m","pc.","CYL","EACH","PC","LT","Pallets","Case","KG","Pallet","Lot","Hour","Lots","PCE","(EA)","PR","PRC","YR","unit","EUX","Units","User","License","STK","pes","PE","GFN","stk."],"isCountry":["Europe","England","UK","Columbus","US","Singapore","Hertfordshire","Stamford","Ireland","Milano","Devon","Oxon","Peruwelz","France","Nottingham","Canada","The Netherlands","South Glos","Gurugram","Manchester","Berkshire","Wereda","Peldanyszam","Draper","Buckinghamshire","Scotland","St Helens","New Yorl","London","East Sussex","Polaska","Myanmar","Japan","Middlesex","Ballygowan","Belgium","Boerne","Germany","Herts","Cambridge","United Kingdom","Esparreguera","Some rse t","Kent","India","Netherlands","Madrid","Amsterdam The Netherlands","South Africa","Alpharetta","Antrim","Nr Knutsford","Pretoria","Australia","Dalla","Italy","New York","United States of America","California","EDINBURGH","Great Britain","Brussels","Whybrow","Krakow","Uruguay","Leeds","New Bury","Washington","NSW","Brentford","Harlow","Switzerland","West Sussex","Hampshire","Surrey","Hong Kong","Middlesbrough","Glasgow","Cheshire","Essex","Koln","Twickenham","Warwick","Liverpool","Lancashire","Yorkshire","Sussex","Tamworth","Hamshipre","Westhoughton","Aldates","Britain","Brooklyn","Peebles","Darmstadt","Buckinghumshipre","Kulmbach","Estate York","Salford","Nertherland","Preston","Huntingdon","Warrington","Orlando","Berkshipre","Co.Louth","Pennsylvania","Bangkok","Runcorn","Stafforshipre","USA","Narthampton","Edingurgh","Wycombe","Penarth","Staffordshire","Swindon","Dublin","Netherland","BRISTOL","Dorset","Lincolnshipre","Brasil","Masku","Caerphilly","Aldershot","Wrexham","Birmingham","Durban","Slough","Pepper lane","Holywood","Denmark","Bolton","Shropshire","Albans","West Midlands","Hempstead","Cumbernauld","Kholin","West Yorkshire","Cheshipre","Derby","Kenya","Basingstoke","Northamptonshipre","Westfallca","Ethiopia","Korea","CA","Nevada","Chicago","Las vegas","NV","IND","AUS"],"isKeyword":["invoice","inv","quantity","qty","item","po","number","no.","description","desc","payment","terms","net","days","due","date","dt","reference","vat","tax","total","unit","units","price","amount","amt","bill","ship","billing","shipping","address","payment","reference","value","unit","purchase","ref","uom","weight","wt","services","service","fee","charge","charges","gst","rate","currency","order","discount","subtotal","sub-total","ship","balance","code","period","bank","remittance","account","advice","customer"]}

foo = lambda x: pd.Series([i for i in x])
DF_TIME = pd.DataFrame(columns=["Funaction Name", "Time (in sec)"])

def timing(f):
    """
    Function decorator to get execution time of a method
    :param f:
    :return:
    """

    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        DF_TIME.loc[len(DF_TIME)] = [f.__name__, (time2 - time1)]
        print('{:s}: {:.3f} sec'.format(f.__name__, (time2 - time1)))
        return ret

    return wrap

@timing
def get_list_blobs_in_container(start_name):
    """
    Returns list of blobs in the container which starts with given name
    Can be used to list all the files inside a folder
    """
    blobs = container_client.list_blobs(name_starts_with=start_name)
    return blobs

@timing
def copy_file_to_local(blobname,local_directory):
    """
    Function to Copy file to local from blob storage
    """
    if blobname != '':
        try:
            filename = os.path.basename(blobname)
            localpath = os.path.join(local_directory,filename)
            blob_client = blob_service_client.get_blob_client(container=container,
                blob=blobname)

            with open(localpath, "wb") as download_file:
                        download_file.write(blob_client.download_blob().readall())

            return localpath
        except Exception as e:
            print("\t\t",blobname, e)
            return ''
        
    else:
        return ''

def is_alpha_numeric(text):
    """ 
    Checks wheter a string a alphanumeric (Letters and Digit) or not    
    Return: 1 when Alphanumeric, 0 otherwise    
    """
    return 1 if not(pd.isna(text)) and text.isalnum() else 0


def is_alpha(text):
    """    
    Checks wheter a string a alph (Letters) or not  
    Return: 1 when Alpha, 0 otherwise   
    """
    return 1 if not(pd.isna(text)) and str(text).isalpha() else 0


def noOfPuncs(text):
    """ 
    Count Number of colons, semicolons, hypens, commas and periods in a text    
    Return: Returns total and individual counts 
    """
    count = 0
    colon = 0
    semicolon = 0
    hyphen = 0
    comma = 0
    period = 0

    if not type(text) == float:
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


def is_amount(s):
    """ 
    Checks whether passed string is valid amount or not 
    Returns: 1 if amount, 0 otherwise   
    """
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
    return 0


def is_ID(row):
    """ 
    Checks whether text is ID or not    
    Conditions for being ID: Lenght of digit should be greater than length of letters   
    Total length of text should be greater than 7   
    Returns: 1 if ID, 0 otherwise   
    """
    if (not pd.isna(row['text'])) and row["len_digit"] > 0 and row["len_digit"] > row["len_alpha"] and len(str(row['text'])) > 7 and row["DATE"] == 0 and row["is_email"] == 0:
        list_id = 1
    else:
        list_id = 0
    
    return list_id

def is_label(feature):
    """    
    Checks whether a text belongs to predefined label or not    
    """
    for i in labelKeywords:
        feature[i] = [1 if t in labelKeywords[i] else 0 for t in [text for text in feature['text'].str.lower()] or 0]

    return feature

@timing
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

    AA = pd.merge(temp,
                  DF[['OriginalFile','page_num', 'line_num', 'word_num', 'text', 'top',
                      'bottom', 'left', 'right']],
             on=['OriginalFile', 'page_num', 'line_num', 'word_num'],
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

@timing
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
        temp.page_num AS page_num,
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
        temp.page_num = DF.page_num AND
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
                  DF[['OriginalFile','page_num', 'line_num', 'word_num', 'text', 'top',
                      'bottom', 'left', 'right']],
             on=['OriginalFile', 'page_num', 'line_num', 'word_num'],
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
                  DF[['OriginalFile','page_num', 'line_num', 'word_num', 'text', 'top',
                      'bottom', 'left', 'right']],
             on=['OriginalFile', 'page_num', 'line_num', 'word_num'],
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

@timing
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
            temp.page_num AS page_num,
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
            temp.page_num = DF.page_num AND
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
                  DF[['OriginalFile','page_num', 'line_num', 'word_num', 'text', 'top',
                      'bottom', 'left', 'right']],
             on=['OriginalFile', 'page_num', 'line_num', 'word_num'],
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
                  DF[['OriginalFile','page_num', 'line_num', 'word_num', 'text', 'top',
                      'bottom', 'left', 'right']],
             on=['OriginalFile', 'page_num', 'line_num', 'word_num'],
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

@timing
def extract_text_features_(DF):
    DF.reset_index(inplace=True)
    find_left_right_text(DF, 1, "left")
    find_left_right_text(DF, 2, "left")
    find_left_right_text(DF, -1, "right")
    find_left_right_text(DF, -2, "right")
    find_top_text(DF)
    find_bottom_text(DF)
    del DF['index']

@timing
def extract_number_words_(df):
    """
    Extracts features related to number of words in the line
    :param df:
    :return:
    """
    temp = df.groupby(["OriginalFile", "page_num", "line_num"])[['text']].count().reset_index()
    temp = temp.rename(columns={'text': 'words_on_line'})

    df = pd.merge(df, temp, on=['OriginalFile', 'page_num', 'line_num'], how='left')
    return df

@timing
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

@timing
def extract_ner_spacy(df):
    """
    Extract Named Entity Recognition from Spacy
    :param df:
    :return:
    """
    df['NER_Spacy'] = "UKWN"

    set_labels = set(cat_encoding['NER_Spacy'])
    for index, row in df.iterrows():
        text = str(row['text']).lower()
        doc = nlp(text)
        try:
            for ent in doc.ents:
                label = ent.label_
                if label in set_labels:
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

@timing
def extract_is_email(df):
    """
    Extract whether text is in email format or not
    :param df:
    :return:
    """
    df['is_email'] = df['text'].apply(check_email)

@timing
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

    # df.drop(columns = list(set(list(df.columns)) - set(model_features)), axis = 1, inplace = True)
    return df, model_features

@timing
def wordBoundingText(DF):
    DF_new = pd.DataFrame()
    tempar = pd.DataFrame()

    for i in DF["OriginalFile"].unique():
        temp = DF['OriginalFile'] == i
        tempar = DF[temp].copy()
        tempar[neighbWords] = tempar.apply(findWordsClose,args=(tempar,),axis = 1)

        if DF_new.shape[0] == 0:
            DF_new = tempar
        else:
            DF_new = DF_new.append(tempar)

    return DF_new

def wordshape(text):
    if not(pd.isna(text)):
        t1 = re.sub('[A-Z]', 'X',text)
        t2 = re.sub('[a-z]', 'x', t1)
        return re.sub('[0-9]', 'd', t2)
    return text

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
        print("\t\t",e,"isOverlap")
        return False

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

def findWordsClose(row,df):

    pixelThresh = .05
    sideThesh = 0.01

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
    sdLeft = row["left"] - sideThresh
    sdRight = row["right"] + sideThresh
    dffilt = df[(df["bottom"] >= top) & (df["bottom"] < row["top"])]
    #Sort the dataframe so that the closest to the bounding box is on top
    dffilt = dffilt.sort_values(["bottom"], ascending = False)
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [row["left"],top,row["right"],row["bottom"]]
        rect1 = [sdLeft,top,sdRight,row["bottom"]]
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
    sdLeft = row["left"] - sdThresh
    sdRight = row["right"] + sdThresh
    dffilt = df[(df["top"] <= bottom) & (df["top"] > row["bottom"])]
    #Sort the dataframe so that the closest to the bounding box is on top
    dffilt = dffilt.sort_values(["top"], ascending = True)
    cnt = 0
    for i,j in dffilt.iterrows():
        rect1 = [row["left"],row["top"],row["right"],bottom]
        rect1 = [sdLeft,row["top"],sdRight,bottom]
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
    #Sort the dataframe so that the closest to the bounding box is on top
    dffilt = dffilt.sort_values(["right"], ascending = False)
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
    #Sort the dataframe so that the closest to the bounding box is on top
    dffilt = dffilt.sort_values(["left"], ascending = True)
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

@timing
def getLineInfo(DF, imagepath, page_count):
    DF_new = pd.DataFrame()
    tempar = pd.DataFrame()

    ret, imgs = cv2.imreadmulti(imagepath)

    for i in range(page_count):

        if len(imgs[i].shape) == 3:
            imgs[i] = cv2.cvtColor(imgs[i], cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(imgs[i],3)
        pre = cv2.threshold(blur, 210, 255,
                            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        vlines, hlines = findLines(pre)
        height = pre.shape[0]
        width = pre.shape[1]

        hlines = [(hline[0] / width,hline[1] / height,hline[2] / width,hline[3] / height) for hline in hlines]
        vlines = [(vline[0] / width,vline[1] / height,vline[2] / width,vline[3] / height) for vline in vlines]

        file_split = os.path.basename(imagepath).split(".")
        filename = file_split[0]
        file_extn = "."+file_split[-1]

        temp = DF['OriginalFile'] == filename+"_"+str(i)+file_extn
        tempar = DF[temp].copy()
        
        if tempar.shape[0] > 0:
            tempar[lineInfo] = tempar.apply(findLinesClose, args=(hlines,vlines),axis = 1)
            if DF_new.shape[0] == 0:
                DF_new = tempar
            else:
                DF_new = DF_new.append(tempar)

    return DF_new

@timing
def extract_bounding_text_features(dframe1):
    for i in neighbWordsVec:
        temp_list = []
        dframe1[i+"_"+str("is_alpha_numeric")] = dframe1[i].apply(is_alpha_numeric)
        dframe1[i+"_"+str("is_alpha")] = dframe1[i].apply(is_alpha)
        dframe1[i+"_"+str("is_amount")] = dframe1[i].apply(is_amount)
        #dframe1[i+"_"+str("wordshape")] = dframe1[i].apply(wordshape)
        dframe1[i+"_"+str("noOfPuncs_list")] = dframe1[i].apply(noOfPuncs)
        for j in noOfPuncs_list:
            temp_list.append(str(i)+"_"+str(j))
        dframe1[temp_list] = dframe1[i+"_"+str("noOfPuncs_list")].apply(foo)
        del dframe1[i+"_"+str("noOfPuncs_list")]
        #dframe1['vector'] = dframe1[i+"_"+str("wordshape")].apply(w2v)
        #temp_list = []
        #for j in shape_emb:
        #    temp_list.append(str(i)+"_"+str(j))
        #dframe1[temp_list] = dframe1["vector"].apply(foo)

    return dframe1

@timing
def extract_text_specific_features(df):
    
    df["wordshape"] = df['text'].apply(wordshape)
    df["is_ID"] = df.apply(is_ID, axis=1)
    
    
    df["is_alpha_numeric"] = df['text'].apply(is_alpha_numeric)
    df["is_alpha"] = df['text'].apply(is_alpha)
    df["is_amount"] = df['text'].apply(is_amount)
    df["noOfPuncs_list"] = df['text'].apply(noOfPuncs)
    df[noOfPuncs_list] = df["noOfPuncs_list"].apply(foo)
    del df['noOfPuncs_list']

    return df

def get_unique_file(OriginalFile):
    file_split = OriginalFile.split("_")
    file_extn = "."+file_split[-1].split(".")[-1]
    return '_'.join(file_split[:-1]) + file_extn

@timing
def get_file_page_count(df):
     
    df['unique_file'] = df['OriginalFile'].apply(get_unique_file)

    uniqueFile = list(df['unique_file'].unique())
    client = df.loc[0]['Client']
    Format = df.loc[0]['Format']
    Parent_Folder = img_folder

    page_count = {}
    
    for file in uniqueFile:
        no_of_page = len(df[df['unique_file'] == file]['OriginalFile'].unique())
        filepath = '/'.join([Parent_Folder,client,Format,file])
        page_count[file] = {"blobpath":filepath,"pages":no_of_page}
    return page_count

@timing
def extract_image_features(df):
    files_dict = get_file_page_count(df)
    unique_files = list(files_dict.keys())

    temp_df = pd.DataFrame()
    temp_df_final = pd.DataFrame()

    for file in unique_files:
        image_blobpath = files_dict[file]['blobpath']
        image_page_count = files_dict[file]['pages']
        
        imageFilepath = copy_file_to_local(image_blobpath,localWorkingDirectory)
        print("\tCurrent Image:- ",os.path.basename(imageFilepath))
        print("\tNo of pages:- ",image_page_count)
        if imageFilepath != '':
            temp_df = getLineInfo(df, imageFilepath, image_page_count)
            temp_df_final = temp_df_final.append(temp_df)
            #print("Each File",type(temp_df),temp_df.shape)
        else:
            print("\t\tNo Image File found for ",image_blobpath)

    temp_df_final = temp_df_final.drop('unique_file', axis=1)
    
    return temp_df_final

@timing
def get_file_info(df):
    print("File Count:- ",len(list(df['OriginalFile'].apply(get_unique_file).unique())))
    test = get_file_page_count(df)
    for key in test:
        print("\tFilename:- ",key,"No of Pages", test[key]['pages'])


@timing
def process_df_for_feature_extraction(df):

    get_file_info(df)
    
    df = df.loc[df['conf'] != '-1']
    df = df.reset_index(drop=True)
    df['conf'] = df['conf'].astype(float)
    extract_text_features_(df)
    df = extract_number_words_(df) 
    extract_token_specific_features(df)
    extract_ner_spacy(df)
    extract_is_email(df)
    
    df, model_features = extract_model_features(df)
        
    ### Recently added
    df = extract_text_specific_features(df)
    df = wordBoundingText(df)
    
    df = extract_bounding_text_features(df)

    # df = is_label(df)

    df = extract_image_features(df)
    
    #print(type(temp_df_final),temp_df_final,temp_df_final.shape)
    df.sort_values(by=['OriginalFile','page_num','top','left'], inplace=True)
    
    return df


blobs = get_list_blobs_in_container(csv_folder)

#testset = ["Format_2310.csv","Format_925.csv","Format_38.csv","Format_809.csv","Format_635.csv","Format_480.csv","Format_100.csv","Format_1000.csv","Format_999.csv","Format_124.csv"]

for b in blobs:
    #print(b)
    if ".csv" in b["name"]:
        file_name_splitted = b["name"].split('/')
        if True or file_name_splitted[-1] in testset:
            client_name = file_name_splitted[1]
            print("\n########### Started ###########")
            print("Current Format:- ", os.path.basename(b["name"]))
            localpath = copy_file_to_local(b["name"],localWorkingDirectory)
            
            if localpath != "":
                df=pd.read_csv(localpath,index_col=0)
                df = process_df_for_feature_extraction(df)
                df.to_csv(localpath)
                
                filename = os.path.basename(localpath)
                out_csv_file_name = os.path.join(out_feature_folder, client_name)
                out_csv_file_name = os.path.join(out_csv_file_name, filename)

                blob_client = blob_service_client.get_blob_client(container=container,
                    blob=out_csv_file_name)
                try:
                    print("Uploading to Azure Storage as blob: " + out_csv_file_name, df.shape)
                    # Upload the created file
                    # with open(localpath, "rb") as data:
                    #     blob_client.upload_blob(data, overwrite=True)
                    DF_TIME.to_csv("Feature_Extraction_Logs.csv")
                    print("########### Ended ###########")
                except Exception as e:
                    print("\t\t",e)

                    pass
                #os.remove(localpath)

#DF_TIME.to_csv("Feature_Extraction_Logs.csv")
