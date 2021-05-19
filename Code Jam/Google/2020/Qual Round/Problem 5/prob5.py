# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 23:01:57 2020

@author: Hari
"""

import itertools as it
from collections import Counter
noCases = int(input())

for caseN in range(noCases):
    caseNo = caseN + 1
    sCaseNo = str(caseNo)
    l = input().split(" ")
    n = int(l[0])
    k = int(l[1])
    g = list(range(1,n+1))
    possible = False
    for t in it.combinations_with_replacement(g,n):
        if sum(t) == k:
            c = Counter(t)
            keys_ = list(c.keys())
            vals_ = list(c.values())
            if (len(keys_) == 2) and (1 in vals_):
                possible = False
            else:
                possible = True
                break

    if not possible:
        print("Case #" + sCaseNo + ": IMPOSSIBLE")
    else:
        print("Case #" + sCaseNo + ": POSSIBLE")



