# -*- coding: utf-8 -*-
"""
Created on Mon May 17 19:06:51 2021

@author: Hari
"""

from PIL import Image
from pyzbar.pyzbar import decode
import os

folderpath = r"D:\Invoice Data Extraction\TAPP 3.0\Demos\Coke Demo\May17_All60"
files = os.listdir(folderpath)

decoded = {}

for f in files:
    if ".tif" in f.lower():
        filepath = os.path.join(folderpath,f)
        img = Image.open(filepath)
        decoded[f] = decode(img)

decoded_out = {k:v for k,v in decoded.items() if len(v) != 0}

decoded_fail = {k:v for k,v in decoded.items() if len(v) == 0}



