# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 10:48:40 2021

@author: Hari
"""

import math

def isEven(n):
    return list(str(n))[::-1][0] in ['0','2','4','6','8']

def isPrime(n):

    if n in [2,3,5,7]:
        return 1
    elif n < 2:
        return 0
    elif isEven(n):
        return 0
    else:
        ld = math.trunc(math.sqrt(n))

        if isEven(ld):
            ld -= 1

        divs = list(range(ld,1,-2))
        for div in divs:
            if n % div == 0:
                return 0
        return 1

def main():

    # Write code here 
    no_samples = int(input())
    for i in range(no_samples):
        inp_range = input().split(" ")
        l_range = int(inp_range[0])
        u_range = int(inp_range[1])
        prime1 = 1
        prime2 = 0
        
        if l_range == u_range:
            if isPrime(l_range):
                print(0)
                continue
            else:
                print(-1)
                continue
        else:
            for j in range(l_range,u_range + 1):
                if isPrime(j):
                    prime1 = j
                    prime2 = j
                    break
            for k in range(u_range, l_range - 1, -1):
                if isPrime(k):
                    prime2 = k
                    break
        print(prime2 - prime1)

main()

