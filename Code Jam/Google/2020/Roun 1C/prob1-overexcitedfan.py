# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 12:48:46 2020

@author: Hari
"""

#Get number of test cases
noCases = int(input())

for caseN in range(noCases):

    #Start the case number as 1-based index
    caseNo = caseN + 1
    sCaseNo = str(caseNo)

    xyPath = input().split(" ")
    x = int(xyPath[0])
    y = int(xyPath[1])
    paths = list(xyPath[2])

    coords = []
    over = False
    for pathind,path in enumerate(paths):
        if path == "N":
            y += 1
        elif path == "E":
            x += 1
        elif path == "W":
            x -= 1
        elif path == "S":
            y -= 1
        coords.append((x,y))
        pathsum = abs(x) + abs(y)
        minutes = pathind + 1
        if minutes >= pathsum:
            print("Case #" + sCaseNo + ": " + str(minutes))
            over = True
            break
    if not over:
        print("Case #" + sCaseNo + ": IMPOSSIBLE")


