# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 21:31:29 2020

@author: Hari
"""

import pandas as pd
import datetime


df = pd.read_excel("Tagging_Status_2_" + str(datetime.datetime.now().date()) + ".xlsx")
#df = pd.read_excel("Tagging_Status_1_2020-06-15.xlsx")

cols = list(df.columns.values)

linecols = [col for col in cols if col.startswith("LI_")]
idcols = ["Folder","Tagger Name","Actual File Name","page number",
          "Creation Time","Last Modified","index"]
hdrcols = [col for col in cols if ((col not in linecols) and (col not in idcols)) ]

folders = list(df["Folder"].unique())

rows = []
allfiles = []

for folder in folders:

    dffold = df[df["Folder"] == folder]
    files = list(dffold["Actual File Name"].unique())
    allfiles.extend(files)
    for fil in files:
        dffile = dffold[dffold["Actual File Name"] == fil]
        row = {}
        row["Folder"] = folder
        row["Actual File Name"] = fil

        dfline = dffile[linecols]
        dfline = dfline.dropna(thresh=1)

        if dfline.empty:
            row["line item"] = 0
        else:
            row["line item"] = 1

        dfhdr = dffile[hdrcols]
        dfhdr = dfhdr.dropna(thresh=1)

        if dfhdr.empty:
            row["header"] = 0
        else:
            row["header"] = 1

        row["dup"] = 0
        rows.append(row)

DF = pd.DataFrame(rows)

rowindices = []

for fil in allfiles:
    dffil = DF[DF["Actual File Name"] == fil]

    if dffil.shape[0] > 1:
        dffil["p.tagged"] = dffil["line item"] + dffil["header"]
        dffil = dffil.sort_values(by=["p.tagged"],ascending=False)
        cnt = 0
        for ind,row in dffil.iterrows():
            if cnt > 0:
                fold = row["Folder"]
                filename = fil
                DF.loc[((DF["Folder"] == fold) & (DF["Actual File Name"] == fil)),
                       ['header','line item']] = 0
                DF.loc[((DF["Folder"] == fold) & (DF["Actual File Name"] == fil)),
                       ['dup']] = 1
            cnt += 1

DF["hdr_only"] = 0
DF["line_only"] = 0
DF["untagged"] = 0
DF["tagged"] = 0
DF["hdr_only"] = (DF["line item"] == 0) & (DF["header"] == 1) & (DF["dup"] == 0)
DF["line_only"] = (DF["line item"] == 1) & (DF["header"] == 0) & (DF["dup"] == 0)
DF["untagged"] = (DF["line item"] == 0) & (DF["header"] == 0) & (DF["dup"] == 0)
DF["tagged"] = (DF["line item"] == 1) & (DF["header"] == 1) & (DF["dup"] == 0)

DF = DF.astype({"hdr_only":int,"line_only":int,"untagged":int,"tagged":int})

DF.to_excel("Tagging_Overall_Summary" + str(datetime.datetime.now().date()) + ".xlsx",
            index = False)

