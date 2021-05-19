# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 13:09:05 2020

@author: Hari
"""

noCases = int(input())

for caseN in range(noCases):
    s = input()
    newS = ""
    count = 0
    for d in s:
        k = int(d)
        if k > count:
            newS = newS + (k - count) * "(" + d
        elif k < count:
            newS = newS + (count - k) * ")" + d
        else:
            newS = newS + d
        count = k
    if count > 0:
        newS = newS + count * ")"
    print("Case #" + str(caseN + 1) + ": " + newS)
