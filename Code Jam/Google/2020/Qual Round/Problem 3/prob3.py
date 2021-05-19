# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 14:36:11 2020

@author: Hari
"""

noCases = int(input())

for caseN in range(noCases):
    caseNo = caseN + 1
    sCaseNo = str(caseNo)
    noTasks = int(input())
    c = 0
    j = 0
    impossible = False
    taskTms = []
    for task in range(noTasks):
        times = input().split(" ")
        times = [int(tm) for tm in times]
        taskTms.append((times[0],times[1],task))
    sortTms = sorted(taskTms)

    parents = []
    for st,end,ind in sortTms:
        if c <= st:
            parents.append("C")
            c = end
        elif j <= st:
            parents.append("J")
            j = end
        else:
            impossible = True
            break

    if impossible:
        print("Case #" + str(sCaseNo) + ": IMPOSSIBLE")
    else:
        s = ""
        indices = []
        for tm in taskTms:
            i = sortTms.index(tm)
            s = s + parents[i]
        print("Case #" + str(sCaseNo) + ": " + s)




