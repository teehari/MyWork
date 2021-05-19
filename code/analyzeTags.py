# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:39:03 2020

@author: Hari
"""

import json
import os
import glob
import pandas as pd

inpPath = r"D:\Invoice Data Extraction\TAPP 3.0"
extn = ".vott"

wildCardSrch = inpPath + "\*.vott"

vottFiles = glob.glob(wildCardSrch)

for file in vottFiles:
    f = open(file,"r")
    content = f.read()
    f.close()
    jsonObj = json.loads(content)
    tags = jsonObj["tags"]
    tagNames = []
    compare = {}
    for tag in tags:
        tagNames.append(tag["name"])
    
    compare[os.path.split(file)[1]] = tagNames
    df = pd.DataFrame(compare)
    df.to_csv(os.path.join(inpPath,os.path.split(file)[1] + ".csv"),
                   index = False)

