# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 19:22:52 2021

@author: Hari
"""

import re

def calc_cost(x,y,seq):
    cost = 0
    mod_seq = seq.replace("?","")
    cj_s = re.findall("CJ",mod_seq)
    cost += len(cj_s) * x
    jc_s = re.findall("JC",mod_seq)
    cost += len(jc_s) * y
    return cost

test_cases = int(input())

for case in range(test_cases):
    details = input().split(" ")
    x = int(details[0])
    y = int(details[1])
    seq = details[2]
    cost = calc_cost(x,y,seq)
    print("Case #" + str(case + 1) + ": ", cost)
