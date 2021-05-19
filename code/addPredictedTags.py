# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 19:56:28 2020

@author: Hari
"""

ftrfolder = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\features_old\*"
tagfolder = r"D:\Invoice Data Extraction\TAPP 3.0\lstm_24Apr2020"
filepaths = r"D:\Invoice Data Extraction\TAPP 3.0\lstm_24Apr2020\filepaths_24Apr2020.csv"
result = r"D:\Invoice Data Extraction\TAPP 3.0\lstm_24Apr2020\results"

import glob
import pandas as pd
import os

files = pd.read_csv(filepaths)

for ind, row in files.iterrows():
    tagfile = "file_" + str(row["filenum"]) + ".xlsx"
    filepath = row["files"]
    tagfilepath = os.path.join(tagfolder,tagfile)
    tagdf = pd.read_excel(tagfilepath)
#    tagdf = tagdf[tagdf["Tagindex"] != 2]
    ftrpaths = glob.glob(os.path.join(ftrfolder,filepath + "*"))
    ftrpath = ftrpaths[0]
    ftrdf = pd.read_csv(ftrpath)
    ftrdf = ftrdf[ftrdf["page_num"] == 1]
    text = list(ftrdf["text"])
    label = list(ftrdf["label"])
    text = [text[i] if i <= (len(text) - 1) else "-1" for i in range(3300)]
    label = [label[i] if i <= (len(label) - 1) else "-1" for i in range(3300)]
    tags = list(tagdf["Tagindex"])
    dftags = pd.DataFrame({"Text":text,"Labels":label,"tags":tags})
    resultfile = os.path.split(ftrpath)[1]
    resultfile = os.path.splitext(resultfile)[0] + ".xlsx"
    dftags.to_excel(os.path.join(result,resultfile),index = False)
#    print(ftrdf.shape[0],tagdf.shape[0])




