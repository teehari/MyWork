# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 23:35:37 2020

@author: Hari
"""

import pandas as pd
import json
import os

inp = r"D:\azuretemp\tags.xlsx"
inpdir = r"D:\azuretemp"
df = pd.read_excel(inp)

folders = list(df["folder"])
tags = list(df["tags"])
d = {}

for folder,tag in zip(folders,tags):
    listtags = list(eval(tag))
    fields = []
    for t in listtags:
        field = {}
        field["fieldKey"] = t
        field["fieldType"] = "string"
        field["fieldFormat"] = "not-specified"
        fields.append(field)
        print(t)
    d["fields"] = fields
    j = json.dumps(d)
    with open(os.path.join(inpdir,"fields_"+folder+".json"),"w") as fw:
        fw.write(j)

