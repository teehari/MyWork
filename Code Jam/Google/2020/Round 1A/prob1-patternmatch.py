# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 12:48:46 2020

@author: Hari
"""
#import re

#Get number of test cases
noCases = int(input())

for caseN in range(noCases):
    
    #Start the case number as 1-based index
    caseNo = caseN + 1
    sCaseNo = str(caseNo)
    
    #Get the number of patterns
    noPtns = int(input())

    #Initialize variables
    ptnssplits = []
    regptns = []
    middlewords = ""
    impossible = False
    starts = []
    ends = []
    start = ""
    end = ""
    middle = ""
    finalword = ""

    #Get all the given patterns, beginning word, end word and middle words
    for n in range(noPtns):
        s = input()
        ptnsplit = s.split("*")
        first = ptnsplit[0]
        last = ptnsplit[-1]
        
        if len(first) > len(start):
            if not first.startswith(start):
                impossible = True
                break
            start = first
        else:
            if (len(first) > 0) and (not start.startswith(first)):
                impossible = True
        
        if len(last) > len(end):
            if not last.endswith(end):
                impossible = True
                break
            end = last
        else:
            if (len(last) > 0) and (not end.endswith(last)):
                impossible = True
        regptn = "^" + s.replace("*",".*") + "$"
        regptns.append(regptn)
        ptnssplits.append(ptnsplit)
        #Remove the first and last items from the list
        ptnsplit.pop(0)
        ptnsplit.pop(-1)
        if len(ptnsplit) > 0:
            middle = middle + "".join(ptnsplit)

    #Form a final word
    if not impossible:
        finalword = start + middle + end
        print("Case #" + sCaseNo + ": " + finalword)
    else:
        print("Case #" + sCaseNo + ": *")

    #Check if all the regex patterns satisfy the entire final word
    #If it does, then the given patterns are correct, else impossible
#    for regptn in regptns:
#        wordlist = re.findall(regptn,finalword)
#        if (len(wordlist) != 1) or (wordlist[0] != finalword):
#            impossible = True
#            break

    #If impossible, print * else print finalword
#    if impossible:
#        result = "*"
#    else:
#        result = finalword
#    
#    print("Case #" + sCaseNo + ": " + result)


#    for ptnsplit in ptnssplits:
#        if ptnsplit[0] != "":
#            starts.append(ptnsplit[0])
#        if ptnsplit[len(ptnsplit) - 1] != "":
#            ends.append(ptnsplit[len(ptnsplit) - 1])
#    start = max(starts,key = len)
#    end = max(ends,key=len)
#    ist = starts.index(start)
#    ien = ends.index(end)
#    starts.pop(ist)
#    ends.pop(ien)
#    for st in starts:
#        ptn = re.compile(st + ".")
#        match = bool(re.match(ptn, start))
#        if not match:
#            impossible = True
#            break
#    for en in ends:
#        ptn = re.compile(en + ".")
#        match = bool(re.match(ptn, end))
#        if not match:
#            impossible = True
#            break


#    print("Case #" + sCaseNo + ": " + str(trace) + " " + str(dupRows) + " " + str(dupCols))





