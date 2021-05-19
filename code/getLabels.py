# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:58:29 2020

@author: Hari
"""

src = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\labels"

import json
import pandas as pd
import os
#from pathlib import PurePath
i = 0
rows = []
for root, subfolder, files in os.walk(src):
    i = i + 1
#    if i > 10:
#        break
    if len(files) > 0:
        for filename in files:
            if filename[-12:].upper() == ".LABELS.JSON":
                taggername = os.path.split(root)[1]
                f = open(os.path.join(root,filename),"r")
                o = f.read()
                f.close()
                j = json.loads(o)
                labellist = j["labels"]
                for labelobj in labellist:
                    row = {}
                    labelname = labelobj["label"]
                    values = labelobj["value"]
                    value = ""
                    left = 1.0
                    right = 0.0
                    top = 1.0
                    down = 0.0
                    for val in values:
                        value = value + " " + val["text"]
                        bb = val["boundingBoxes"][0]
                        left = min(left, bb[0], bb[6])
                        right = max(right, bb[2], bb[4])
                        top = min(top, bb[1],bb[3])
                        down = max(down,bb[5],bb[7])
                        page = val["page"]
                    row["filename"] = filename
                    row["taggername"] = taggername
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
df.to_csv(os.path.join(src,"labelAnalysis.csv"),index = False)

