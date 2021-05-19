# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 22:12:06 2021

@author: Hari
"""

from itertools import permutations
import pandas as pd
from collections import Counter as cnt
from win32com.client import Dispatch
from sys import argv

#import en_core_web_sm as en
#nlp = en.load(disable = ['ner','parser'])

s = argv[1]

f = open("d:\\english3.txt","r")
c = f.read()
d = c.split("\n")

def findwords(s):

    l = list(s.lower())
    cnt_s = dict(cnt(s).items())
    dfs = []
    for i in range(len(l),2,-1):
        perms = permutations(l,i)
        words = []
#        pos = []
        for perm in perms:
            word = "".join(perm)
#            nlpword = nlp(word)
            cnt_word = dict(cnt(word).items())
            if word in d:
                if (word not in words) and not (False in set([cnt_word[s] <= cnt_s[s] for s in cnt_word.keys()])):
                    words.append(word)
#                    pos.append(nlpword[0].pos_)
#        dic_word = {str(i):words,str(i)+"_Type":pos}
        dic_word = {str(i):words}
        data = pd.DataFrame(dic_word)
        dfs.append(data)
    df = pd.concat(dfs,axis = 1)
    return df

df = findwords(s)
df.to_csv("d:\\words.csv",index = False)

xl = Dispatch("Excel.Application")
xl.Visible = True
wb = xl.Workbooks.Open(r'd:\words.csv')




