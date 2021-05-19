# -*- coding: utf-8 -*-

src = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\labels"

import json
import pandas as pd
import os
from collections import Counter
import string
import enchant
from nltk.corpus import stopwords

stop = list(stopwords.words("english"))
d = enchant.Dict("en_GB")
punct = list(string.punctuation)
numbers = list(range(10))
numbers = [str(n) for n in numbers]
punct.extend(numbers)

i = 0
rows = []
labels = []
rejected = []


for root, subfolder, files in os.walk(src):
    i = i + 1
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
                    labelname = labelobj["label"]
                    if (labelname[:3].lower() == "lbl") or (labelname[:4].lower() == "hdr_"):
                        values = labelobj["value"]
                        value = ""
                        for val in values:
                            value = val["text"].lower().strip()
                            vals = "".join([" " if g in punct else g for g in value]).split(" ")
                            for v in vals:
                                if (len(v) > 1) and (v not in stop):
                                    labels.append(v)


c = Counter(labels)

words = list(c.keys())
counts = list(c.values())

wordcount = {"word":words,"count":counts}
df = pd.DataFrame(wordcount)
df = df[df["count"] >= 20]

import time
t = str(time.time())
df.to_excel("labels" + t + ".xlsx",index = False)



