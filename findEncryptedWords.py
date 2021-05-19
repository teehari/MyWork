# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 22:12:06 2021

@author: Hari
"""


f = open("d:\\english3.txt","r")
c = f.read()
d = c.split("\n")
length = 6

fiveLetterWords = [w.upper() for w in d if len(w) == length]
print(len(fiveLetterWords))

for word in fiveLetterWords:
    newWord = ""
    for i in range(length):
        ch_num = ord(word[i]) - 65
        newWord += chr(90 - ch_num)
    #print(newWord)
    if newWord in d:
#        print("Found")
        print(word,newWord)
        break

