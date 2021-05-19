# -*- coding: utf-8 -*-

src = r"D:\azuretemp\labels"

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
option = "azline"

i = 0
rows = []
labels = {}
rejected = []


for root, subfolder, files in os.walk(src):
    
    if len(files) > 0:
        for filename in files:
            if filename[-12:].upper() == ".LABELS.JSON":
                i = i + 1
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
                        if option == "word":
                            for val in values:
                                value = val["text"].lower().strip()
                                vals = "".join([" " if g in punct else g for g in value]).split(" ")
                                if option == "word":
                                    for v in vals:
                                        if (len(v) > 1):
                                            if labelname in labels.keys():
                                                labels[labelname].append(v)
                                            else:
                                                labels[labelname] = [v]
                        else:
                            text = ""
                            for value in values:
                                tmp = value["text"].lower().strip()
                                tmp = "".join(["" if g in punct else g for g in tmp])
                                text = text + " " + tmp
                            if labelname in labels.keys():
                                labels[labelname].append(text)
                            else:
                                labels[labelname] = [text]

print(i)
finalLabels = []

for key in labels.keys():
    vals = labels[key]
    c = Counter(vals)
    for k in c.keys():
        finalLabel = {}
        finalLabel["Label"] = key
        finalLabel["Value"] = k
        finalLabel["Count"] = c[k]
        finalLabels.append(finalLabel)


df = pd.DataFrame(finalLabels)
df = df.sort_values(["Label", "Count","Value"], ascending = (True, False, True))

import time
t = str(time.time())
df.to_excel("Labels_FieldWise" + t + ".xlsx",index = False)



