# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 12:48:46 2020

@author: Hari
"""

from collections import Counter
#Get number of test cases
noCases = int(input())

for caseN in range(noCases):

    #Start the case number as 1-based index
    caseNo = caseN + 1
    sCaseNo = str(caseNo)

    cakesDiners = input().split(" ")
    cakes = int(cakesDiners[0])
    diners = int(cakesDiners[1])
    
    degrees = input().split()
    degrees = [int(degree) for degree in degrees]
    sdegrees = sorted(degrees)
    cuts = []
    over = False
    if diners > 1:
        for ind,degree in enumerate(sdegrees):
            lclcuts = 0
            dinersserved = 0
            curdeg = degree
            for deg in sdegrees:
                q = deg // degree
                r = deg % degree

                if (q > 0) and (r == 0):
                    dinersserved += q
                    if dinersserved > diners:
                        dinersserved = diners
                        lclcuts += (q - 1)
                        break
                    elif dinersserved == diners:
                        lclcuts += (q - 1)
                        break
                    else:
                        lclcuts += (q - 1)

#            print("Cuts:",lclcuts,"DinersServed: ",dinersserved, degree)
            if (dinersserved >= diners):
                if lclcuts == 0:
                    print("Case #" + sCaseNo + ": 0")
                    over = True
                    break
                cuts.append(lclcuts)
        if not over:
            if len(cuts) > 0:
                mincuts = min(cuts)
            else:
                mincuts = diners + 1
            if mincuts < diners - 1:
                print("Case #" + sCaseNo + ": " + str(mincuts))
            else:
                cnt = Counter(sdegrees)
                unqdegrees = list(set(sdegrees))
                anCuts = []
                for deg in unqdegrees:
                    c = cnt[deg]
                    q = diners // c
                    r = diners % c
                    if c > 1:
                        mincuts = q * (c - 1) + r
                        anCuts.append(mincuts)
                mincuts = min(anCuts)
                if mincuts < diners - 1:
                    print("Case #" + sCaseNo + ": " + str(mincuts))
                else:
                    print("Case #" + sCaseNo + ": " + str(diners - 1))
    else:
        print("Case #" + sCaseNo + ": 0")


