# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 10:48:40 2021

@author: Hari
"""


virus = "coronavirus"

virus_chars = list(virus)

sub = "crnas"
sub_chars = list(sub)

ind = 0
found = True
prev = ""
for c in sub_chars:
    if c == prev:
        ind += 1
    try:
        ind = virus_chars.index(c,ind)
    except:
        found = False
        break
    prev = c

print("The word ", sub, " is substring:", found)
#
#''' Read input from STDIN. Print your output to STDOUT '''
#    #Use input() to read input from STDIN and use print to write your output to STDOUT

def main():

    # Write code here 
    virus_chars = list(input())
    no_samples = int(input())
    for i in range(no_samples):

        ind = 0
        found = True
        sub_chars = list(input())
        prev = ""
        for c in sub_chars:
            if c == prev:
                ind += 1
            try:
                ind = virus_chars.index(c,ind)
            except:
                found = False
                break
            prev = c
        if found:
            print("POSITIVE")
        else:
            print("NEGATIVE")
    

main()

