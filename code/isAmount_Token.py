# -*- coding: utf-8 -*-
"""
Created on Fri May 14 08:33:49 2021

@author: Hari
"""

import re
import pandas as pd
import json
import time
from requests import get, post
import os


# Endpoint URL
endpoint = r"https://invrecognition.cognitiveservices.azure.com"
apim_key = "f761839e80d744ae95bcfa23a665690c"
post_url = endpoint + "/formrecognizer/v2.0-preview/Layout/analyze"
post_url = endpoint + "/formrecognizer/v2.1/Layout/analyze"

ocr_out_folder = "temp"
mime_type = "image/tiff"

headers = {
    # Request headers
    'Content-Type': mime_type,
    'Ocp-Apim-Subscription-Key': apim_key,
}

def get_analyseLayout(imgpath):

    status = False

    print("Start OCR For file:",imgpath)
    filename = os.path.basename(imgpath)
    ocr_out_path = filename + ".azure.json"

    if os.path.exists(ocr_out_path):
        return True, ocr_out_path

    with open(imgpath, "rb") as f:
        data_bytes = f.read()

    try:
        resp = post(url = post_url, data = data_bytes, headers = headers)
        if resp.status_code != 202:
            print("POST analyze failed:\n%s" % resp.text)
            quit()
        print("POST analyze succeeded:\n%s" % resp.headers)
        get_url = resp.headers["operation-location"]
    except Exception as e:
        print("POST analyze failed:\n%s" % str(e))
        return status, ocr_out_path

    n_tries = 10
    n_try = 0
    wait_sec = 6
    while n_try < n_tries:
        try:
            resp = get(url = get_url,
                       headers = {"Ocp-Apim-Subscription-Key": apim_key})
            resp_json = json.loads(resp.text)
            print(resp.status_code)
            if resp.status_code != 200:
                print("GET Layout results failed:\n%s" % resp_json)
            status = resp_json["status"]
            if status == "succeeded":
                print("Layout Analysis succeeded:\n%s" % imgpath)
                json_text = json.dumps(resp_json)
                with open(ocr_out_path,"w") as f:
                    f.write(json_text)
                f.close()
                status = True
                break
            if status == "failed":
                print("Layout Analysis failed:\n%s" % resp_json)
            # Analysis still running. Wait and retry.
            time.sleep(wait_sec)
            n_try += 1
        except Exception as e:
            msg = "GET analyze results failed:\n%s" % str(e)
            print("ERROR:",msg)

    return status, ocr_out_path


def isTokenAmount(s):

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
        
        t = s.replace(" ","")
        l = len(t)
        
        for ptn in ptns:
            search = re.search(ptn,t)
            if search is not None:
                if search.start() == 0 and search.end() == l:
                    return True
        return False
    except Exception as e:
        print(e)
        return False

def bigrams(texts):
    return [texts[i] + texts[i+1] for i in range(len(texts) - 1)]

def read_ocr_json_file(path):

    def read_result_tag(resultList):
        rows = []
        tokenid = 10000

        for resultobj in resultList:
            pageNo = resultobj["page"]
            lines = resultobj["lines"]
            
            unit = resultobj["unit"]
            unit_in_pixel = 96 if unit == "inch" else 1
            
            width = int(resultobj["width"] * unit_in_pixel)
            height = int(resultobj["height"] * unit_in_pixel)
            lineNo = 0
            for line in lines:
                value = line["text"]
                bb = line["boundingBox"]
                left = min(bb[0] * unit_in_pixel, bb[6] * unit_in_pixel) / width
                right = max(bb[2] * unit_in_pixel, bb[4] * unit_in_pixel) / width
                top = min(bb[1] * unit_in_pixel,bb[3] * unit_in_pixel) / height
                down = max(bb[5] * unit_in_pixel,bb[7] * unit_in_pixel) / height
                # print(pageNo,lineNo,value,left,right,top,down)

                words = line["words"]
                wordNo = 0
                for word in words:
                    row = {}
                    wordValue = word["text"]
                    wordConfidence = word["confidence"]
                    wordBB = word["boundingBox"]
                    wordLeft = min(wordBB[0] * unit_in_pixel, wordBB[6] * unit_in_pixel) / width
                    wordRight = max(wordBB[2] * unit_in_pixel, wordBB[4] * unit_in_pixel) / width
                    wordTop = min(wordBB[1] * unit_in_pixel,wordBB[3] * unit_in_pixel) / height
                    wordDown = max(wordBB[5] * unit_in_pixel,wordBB[7] * unit_in_pixel) / height

                    row["token_id"] = tokenid
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
                    row["text"] = wordValue
                    row["conf"] = wordConfidence
                    row["left"] = wordLeft
                    row["top"] = wordTop
                    row["height"] = wordDown - wordTop
                    row["width"] = wordRight - wordLeft
                    row["right"] = wordRight
                    row["bottom"] = wordDown
                    row["image_height"] = height
                    row["image_widht"] = width
                    row["is_portrait_page"] = 1 if height > width else 0
                    row["page_ratio"] = round(height/width,3)
                    rows.append(row)
                    wordNo = wordNo + 1
                    tokenid = tokenid + 1
                lineNo = lineNo + 1

        return rows

    def read_page_result_tag(pageList, df_ocr):
        df_ocr['rows_in_table'] = 0
        df_ocr['cols_in_table'] = 0
        df_ocr['table_num'] = 0
        df_ocr['row_num'] = 0
        df_ocr['col_num'] = 0
        df_ocr.astype({'line_num': 'int32', 'word_num': 'int32'}).dtypes
        
        rows = []
        for pages in pageList:

            tables = pages['tables']
            for no, table in enumerate(tables):
                table_num = no + 1
                rows_in_table = table['rows']
                cols_in_table = table['columns']
                table_contents = table['cells']

                for cells in table_contents:
                    row_num = cells['rowIndex'] + 1
                    col_num = cells['columnIndex'] + 1
                    cell_text = cells['text']
                    elements = cells['elements']

                    for i, element in enumerate(elements):
                        row = {}
                        element_list = element.split("/")
                        if len(element_list) < 6:
                            continue
                        page_num = int(element_list[2]) + 1
                        line_num = element_list[4]
                        word_num = element_list[6]
                        text = cell_text.split(" ")[i]

                        row['page_num'] = page_num
                        row['line_num'] = line_num
                        row['word_num'] = word_num
                        row['table_num'] = table_num
                        row['row_num'] = row_num
                        row['col_num'] = col_num
                        row['rows_in_table'] = rows_in_table
                        row['cols_in_table'] = cols_in_table
                        row['text'] = text
                        rows.append(row)
                        df_ocr.loc[(df_ocr['page_num'].astype(int) == int(page_num)) & 
                                   (df_ocr['line_num'].astype(int) == int(line_num)) & 
                                   (df_ocr['word_num'].astype(int) == int(word_num)) &
                                   (df_ocr['text'] == text) , 
                                   ['table_num','row_num','col_num','rows_in_table','cols_in_table']
                                  ] = [table_num,row_num,col_num,rows_in_table,cols_in_table]

        return df_ocr

    def correctAmountTokens(df):
        df_copy = df.copy(deep = True)
        try:
            lines = df.groupby(by = ["line_text","line_top","line_left"]).groups
            for line_text,line_top,line_left in lines:
                df_line = df[(df["line_text"] == line_text) & 
                             (df["line_top"] == line_top) &
                             (df["line_left"] == line_left)]
                if df_line.shape[0] == 2:
                    df_line.sort_values(["word_num"],
                                        ascending = [True],
                                        inplace = True)
                    texts = df_line["text"].to_list()
                    text = texts[0] + texts[1]
                    if isTokenAmount(text):
                        line_down = df_line["line_down"]
                        line_right = df_line["line_right"]
                        line_height = df_line["line_height"]
                        line_width = df_line["line_width"]
                        df.loc[(df["line_text"] == line_text) &
                               (df["line_top"] == line_top) &
                               (df["line_left"] == line_left),
                               ["top","bottom","left","right","height","width",
                                "text"]] = [line_top,line_down,line_left,line_right,
                                line_height,line_width,text]
                        print("Text is: ", text, "line text is:", line_text)
                    else:
                        continue
            df.drop_duplicates(["text","top","bottom","left","right"],
                               inplace = True)
            return df
        except Exception as e:
            print(e)
            return df_copy

    def read_lines_from_table(df):

        df["isTableLine"] = 0
        df["noNeighbours"] = 0
        df["isLastAmt"] = 0
        df["tableLineNo"] = 0

        df = df.sort_values(["line_top","line_left"])

        df["temp"] = df["line_top"].astype(str)
        df["temp"] = df["temp"] + "---"
        df["temp"] = df["temp"] + df["line_down"].astype(str)
        df["temp"] = df["temp"] + "---"
        df["temp"] = df["temp"] + df["line_left"].astype(str)
        df["temp"] = df["temp"] + "---"
        df["temp"] = df["temp"] + df["line_right"].astype(str)

        unqs = list(df["temp"].unique())
        df = df.drop(["temp"], axis = 1)

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

        for line_no,unq in enumerate(unqs):
            dims = unq.split("---")

            top = float(dims[0])
            bottom = float(dims[1])
            left = float(dims[2])
            right = float(dims[3])

            dffilt1 = df[(df["line_top"] == top) &
                        (df["line_down"] == bottom) &
                        (df["line_left"] == left) &
                        (df["line_right"] == right) &
                        (df["isTableLine"] == 0)
                        ]

            if dffilt1.shape[0] == 0: # case where isTableLine is already one
                continue   # Still match with next lines

            dffilt2 = df[(((df["line_top"] < bottom) &  
                     (df["line_down"] > top)) | 
                    ((df["line_top"] > bottom) &    
                     (df["line_down"] < top))) &    
                     (df["line_left"] != left) &    
                     (df["line_right"] != right) &  
                     (df["isTableLine"] == 0)   
                     ]
            
            dffilt = dffilt1.append(dffilt2)
            if dffilt.shape[0] > 0:
                dffilt = dffilt.sort_values(["line_left"],
                                            ascending = [False])
                first = dffilt.iloc[0]
                text = first["text"]
                is_amt = int(isAmount(text))
                for ind, row in dffilt.iterrows():
                    df.loc[(df["line_left"] == row["line_left"]) &
                           (df["line_right"] == row["line_right"]) &
                           (df["line_top"] == row["line_top"]) &
                           (df["line_down"] == row["line_down"]),
                           ["isTableLine","noNeighbours",
                           "isLastAmt","tableLineNo"]] = [1,
                            len(dffilt['line_text'].unique()),is_amt,
                            line_no + 1]

        return df


    def token_distances(DF):
    
        df = pd.DataFrame()
        for file in DF['page_num'].unique():
            temp_DF = DF[DF['page_num']==file]
            temp_DF.sort_values(['token_id'], inplace=True)

            # Calculate distances between tokens

            temp_DF['token_dist_next'] = temp_DF['bottom'] - temp_DF['top'].shift(-1)
            temp_DF['token_dist_prev'] = temp_DF['bottom'].shift(1) - temp_DF['top']

            temp_DF['token_dist_forward'] = temp_DF['right'].shift(1) - temp_DF['left']
            temp_DF['token_dist_backward'] = temp_DF['right'] - temp_DF['left'].shift(-1)    

            df = df.append(temp_DF, ignore_index=True)

        df.fillna({'token_dist_prev':0,'token_dist_next':0,
                  'token_dist_forward':0, 'token_dist_backward':0}, inplace=True)

        return df

    def position_binning(DF):
        bins = [0,0.24,0.49,0.74,1]
        labels = [1,2,3,4]
        total_grids = len(labels) ** 2

        # Assign X and Y level bins
        DF['X_text_start'] = pd.cut(DF['left'],bins = bins, labels = labels,include_lowest=True)
        DF['y_text_start'] = pd.cut(DF['top'],bins = bins, labels = labels,include_lowest=True)
        DF['X_text_end'] = pd.cut(DF['right'],bins = bins, labels = labels,include_lowest=True)
        DF['y_text_end'] = pd.cut(DF['bottom'],bins = bins, labels = labels,include_lowest=True)

        DF['X_line_start'] = pd.cut(DF['line_left'],bins = bins, labels = labels,include_lowest=True)
        DF['y_line_start'] = pd.cut(DF['line_top'],bins = bins, labels = labels,include_lowest=True)
        DF['X_line_end'] = pd.cut(DF['line_right'],bins = bins, labels = labels,include_lowest=True)
        DF['y_line_end'] = pd.cut(DF['line_down'],bins = bins, labels = labels,include_lowest=True)

        # Calculate Grid value
        y_inc = 0
        for y_bin in range(1,len(labels)+1):
            for x_bin in range(1,len(labels)+1):
                grid_value = (int(x_bin)+y_inc)/total_grids

                DF.loc[((DF['y_text_start'] == y_bin) & (DF['X_text_start'] == x_bin)), 'text_start_grid'] = grid_value
                DF.loc[((DF['y_text_end'] == y_bin) & (DF['X_text_end'] == x_bin)), 'text_end_grid'] = grid_value
                DF.loc[((DF['y_line_start'] == y_bin) & (DF['X_line_start'] == x_bin)), 'line_start_grid'] = grid_value
                DF.loc[((DF['y_line_end'] == y_bin) & (DF['X_line_end'] == x_bin)), 'line_end_grid'] = grid_value

            y_inc += len(labels)

        return DF

    f = open(path, "r", encoding = "utf8")
    o = f.read()
    f.close()
    j = json.loads(o)
    resultList = j["analyzeResult"]["readResults"]
    pageList = j["analyzeResult"]["pageResults"]

    rows = read_result_tag(resultList)
    if len(rows) == 0 :
        return None

    df = pd.DataFrame(rows)
    df = read_page_result_tag(pageList, df)
    df = correctAmountTokens(df)

    df = read_lines_from_table(df)
    df = token_distances(df)
    df = position_binning(df)
    df.to_csv("result.csv")

    return df

r = get_analyseLayout(r"D:\Invoice Data Extraction\TAPP 3.0\Demos\Coke Demo\OCRISSUES\Food and INNS\3184_005.tif")

df = read_ocr_json_file(r[1])

