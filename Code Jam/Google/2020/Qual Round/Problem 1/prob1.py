# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 12:48:46 2020

@author: Hari
"""


noCases = int(input())

for caseN in range(noCases):
    caseNo = caseN + 1
    sCaseNo = str(caseNo)
    lMatrix = int(input())
    trace = 0
    dupRows = 0
    dupCols = 0
    cols = {}
    for ind in range(lMatrix):
        cols[ind] = []
    for rowN in range(lMatrix):
        row = input().split(" ")
        row = [int(r) for r in row]
        trace += row[rowN]
        if len(list(set(row))) != len(row):
            dupRows += 1
        for ind in range(lMatrix):
            cols[ind].append(row[ind])
    for ind in range(lMatrix):
        col = cols[ind]
        if len(list(set(col))) != len(col):
            dupCols += 1
    print("Case #" + sCaseNo + ": " + str(trace) + " " + str(dupRows) + " " + str(dupCols))

    
    
    