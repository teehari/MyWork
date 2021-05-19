# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 19:03:41 2021

@author: Hari
"""

import math

def factors(n):
    sqrn = math.trunc(math.sqrt(n))
    facts = []
    for num in range(2,sqrn+1):
        if n % num == 0:
            facts.append(num)
            facts.append(n // num)
    return sorted(list(set(facts)))

def gcd(*args):
    fact_list = []
    for num in args:
        facts = [1] + factors(num) + [num]
        fact_list.append(set(facts))
    res = []
    for i in range(len(fact_list)-1):
        res.extend(list(fact_list[i].intersection(fact_list[i+1])))
    return max(res)

def lcm(*args):
    prod = 1
    for num in args:
        prod *= num
    ans = prod
    prod_facts = factors(prod)
#    print(prod_facts)
    for fact in prod_facts:
        tmp = prod // fact
        mods = [tmp % num for num in args]
#        print(mods,tmp,fact)
        if mods == [0] * len(args):
            ans = tmp
#            print("Inside the condition: ", tmp, mods)
    return ans

print(lcm(11,12,13,14))