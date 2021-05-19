# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 20:39:13 2020

@author: Hari
"""

from azure.storage.blob import BlockBlobService
import os

root = r"D:\Invoice Data Extraction\TAPP 3.0\Sample Model"
imgPath = os.path.join(root,"images")
ocrPath = os.path.join(root,"ocrs")
labelPath = os.path.join(root,"labels")

os.makedirs(imgPath, exist_ok = True)
os.makedirs(ocrPath, exist_ok = True)
os.makedirs(labelPath, exist_ok = True)

BLOB_ACCOUNT_NAME = "tapp2data"
BLOB_ACCOUNT_KEY1 = "C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg=="
container = "formatseperator"

blobService = BlockBlobService(account_name=BLOB_ACCOUNT_NAME,account_key=BLOB_ACCOUNT_KEY1)
allBlobs = blobService.list_blobs(container)

for blob in allBlobs:
    blobName = blob.name
    blobPath = ""
    if blobName.endswith(".TIF"):
        subFolder = blobName.split("/")[0]
        os.makedirs(os.path.join(imgPath,subFolder),
                    exist_ok = True)
        imgPath_1 = os.path.join(imgPath,subFolder)
        blobPath = os.path.join(imgPath_1,blobName.split("/")[1])
    elif blobName.endswith(".ocr.json"):
        subFolder = blobName.split("/")[0]
        os.makedirs(os.path.join(ocrPath,subFolder),
                    exist_ok = True)
        ocrPath_1 = os.path.join(ocrPath,subFolder)
        blobPath = os.path.join(ocrPath_1,blobName.split("/")[1])
    elif blobName.endswith(".labels.json"):
        subFolder = blobName.split("/")[0]
        os.makedirs(os.path.join(labelPath,subFolder),
                    exist_ok = True)
        labelPath_1 = os.path.join(labelPath,subFolder)
        blobPath = os.path.join(labelPath_1,blobName.split("/")[1])

#    if (blobPath != "") and not (os.path.isfile(blobPath)):
    if (blobPath != ""):
        blobService.get_blob_to_path(container, blob.name,blobPath)


