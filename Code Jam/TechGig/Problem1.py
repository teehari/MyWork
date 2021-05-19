# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:07:07 2020

@author: Hari
"""

def main():

 # Write code here 
 noIngred = int(input())
 qtsPow = input().split(" ")
 qtsPow = [int(qt) for qt in qtsPow]
 qtsAvl = input().split(" ")
 qtsAvl = [int(qt) for qt in qtsAvl]
 noPow = min([(qtAvl // qtsPow[i]) for i,qtAvl in enumerate(qtsAvl)])
 print(noPow)

main()