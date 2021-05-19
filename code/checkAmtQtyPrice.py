# -*- coding: utf-8 -*-
"""
Created on Wed May 19 17:37:32 2021

@author: Hari
"""

from itertools import combinations
import numpy as np

l = ["36","4611407","34039900","4", "8476.26","9,8476.25",
     "305145.36","27,463.08","9,27,463.08","0","360071.52"]

l = [round(float(i.replace(",","")),2) for i in l]

l_comb = list(combinations(l, 2))

p = list(np.product(np.array(l_comb),axis = 1))

[l.index(j) for j in p if j in l]

