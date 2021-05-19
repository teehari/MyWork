# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 12:48:46 2020

@author: Hari
"""
#import re

#
#for caseN in range(noCases):
#    
#    #Start the case number as 1-based index
#    caseNo = caseN + 1
#    sCaseNo = str(caseNo)
#    
#    #Get the number of patterns
#    noPtns = int(input())
#
#    #Initialize variables
#    ptnssplits = []
#    regptns = []
#    middlewords = ""
#    impossible = False
#    starts = []
#    ends = []
#    start = ""
#    end = ""
#    middle = ""
#    finalword = ""
#
#    #Get all the given patterns, beginning word, end word and middle words
#    for n in range(noPtns):
#        s = input()
#        ptnsplit = s.split("*")
#        first = ptnsplit[0]
#        last = ptnsplit[-1]
#        
#        if len(first) > len(start):
#            if not first.startswith(start):
#                impossible = True
#                break
#            start = first
#        else:
#            if (len(first) > 0) and (not start.startswith(first)):
#                impossible = True
#        
#        if len(last) > len(end):
#            if not last.endswith(end):
#                impossible = True
#                break
#            end = last
#        else:
#            if (len(last) > 0) and (not end.endswith(last)):
#                impossible = True
#        regptn = "^" + s.replace("*",".*") + "$"
#        regptns.append(regptn)
#        ptnssplits.append(ptnsplit)
#        #Remove the first and last items from the list
#        ptnsplit.pop(0)
#        ptnsplit.pop(-1)
#        if len(ptnsplit) > 0:
#            middle = middle + "".join(ptnsplit)
#
#    #Form a final word
#    if not impossible:
#        finalword = start + middle + end
#        print("Case #" + sCaseNo + ": " + finalword)
#    else:
#        print("Case #" + sCaseNo + ": *")


import numpy as np
def avgNbrs(arr1):

    arr1 = arr1.astype(float)
    arr = arr1.copy()
    w = arr.shape[1]
    h = arr.shape[0]
    
    for i in range(w):
        for j in range(h):
            cell = arr1[j,i]

            if cell > 0:
                rt = arr1[j,i+1:]
                rtNbr = 0
                if rt.shape[0] > 0:
                    nbrind = np.where(rt > 0)
                    if len(nbrind[0]) > 0:
                        rtNbr = rt[nbrind[0][0]]

                lf = arr1[j,-arr1.shape[1]:i][::-1]
                lfNbr = 0
                if lf.shape[0] > 0:
                    nbrind = np.where(lf > 0)
                    if len(nbrind[0]) > 0:
                        lfNbr = lf[nbrind[0][0]]

                tp = arr1[-arr1.shape[0]:j,i][::-1]
                tpNbr = 0
                if tp.shape[0] > 0:
                    nbrind = np.where(tp > 0)
                    if len(nbrind[0]) > 0:
                        tpNbr = tp[nbrind[0][0]]

                dn = arr1[j+1:,i]
                dnNbr  = 0
                if dn.shape[0] > 0:
                    nbrind = np.where(dn > 0)
                    if len(nbrind[0]) > 0:
                        dnNbr = dn[nbrind[0][0]]

                tot = 0
                n = 0
                if rtNbr > 0:
                    tot += rtNbr
                    n += 1
                if lfNbr > 0:
                    tot += lfNbr
                    n += 1
                if tpNbr > 0:
                    tot += tpNbr
                    n += 1
                if dnNbr > 0:
                    tot += dnNbr
                    n += 1
                if cell > 0:
                    tot += cell
                    n += 1

                if n > 0:
                    avg = (tot * 1.)/n
                    arr[j,i] = avg

    return arr

def findIntLvl(arr):
    
    lclarr = arr.copy()
    intlvl = 0    
    intlvl += np.sum(lclarr)
    loopon = True

    while loopon:
        avgarr = avgNbrs(lclarr)
        bitarr = (lclarr >= avgarr).astype(float)
        elmarr = lclarr * bitarr
        sameornot = np.unique((lclarr == elmarr))
        if (sameornot.shape[0] == 1) and (sameornot[0] == True):
            loopon = False
        else:
            lclarr = elmarr
            intlvl += np.sum(lclarr)
    return intlvl

#Get number of test cases
noCases = int(input())

for caseN in range(noCases):
    
    #Start the case number as 1-based index
    caseNo = caseN + 1
    sCaseNo = str(caseNo)

    rc = input().split(" ")
    r = int(rc[0])
    c = rc[1]

    l = []
    for i in range(r):
        row = input().split(" ")
        row = [int(itm) for itm in row]
        l.append(row)
    
    a = np.array(l)
    a = a.astype(float)
    b = findIntLvl(a)
    
    print("Case #" + sCaseNo + ": " + str(int(b)))


#l = [[1,1,1],[1,2,1],[1,1,1]]
#l = [[15]]
#l = [[3,1,2]]
#l = [[1,2,3]]
#a = np.array(l)
#a = a.astype(float)
#b = findIntLvl(a)
#
#
#print(int(b))


