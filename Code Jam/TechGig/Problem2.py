# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:07:07 2020

@author: Hari
"""

def main():
    # Write code here 
    noTestCases = int(input())
    for i in range(noTestCases):
        noOfPows = int(input())
        gteams = input().strip().split(" ")
        gteams = sorted([int(i) for i in gteams])
        oppteams = input().strip().split(" ")
        oppteams = sorted([int(i) for i in oppteams])
        counter = 0
        for opp in oppteams:
            ms = [gteam for gteam in gteams if opp < gteam]
            if len(ms) > 0:
                m = min(ms)
                mindex = gteams.index(m)
                gteams.pop(mindex)
                counter += 1
        print(counter)

main()