# -*- coding: utf-8 -*-
"""
Created on Tue May 19 19:48:30 2020

@author: Hari
"""


from azure.storage.blob import BlobServiceClient
import os
#import pandas as pd
#import datetime
import time

localtempfolder = r"d:\azuretemp"
tempname = str(time.time())
tempfolder = os.path.join(localtempfolder,tempname)
os.makedirs(tempfolder,exist_ok=True)

conn_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container = "formatseperator"
container_client = blob_service_client.get_container_client(container)

source = "Review_9"
#Get all the blobs from the container
blobs = container_client.list_blobs(name_starts_with=source + "/")
#lblobs = list(blobs)
#filecount = len(lblobs)
#noOfSubfolders = filecount // 30
blobnames = set([])
fullnames = []
import re

for blobindex,b in enumerate(blobs):
    blobname = b["name"]
    filename = blobname.split("/")[-1]
    splitblobname = re.split("_[0-9]{1,3}.TIF",filename)
    actualblobname = splitblobname[0]
    blobnames.add(actualblobname)
    fullnames.append(blobname)

blobnames = list(blobnames)
foldername = ""
for blobindex,b in enumerate(blobnames):
    actfilename = b
    fullblobnames = [name for name in fullnames if actfilename in name]

    for blobname in fullblobnames:
        blob_client = blob_service_client.get_blob_client(container=container,
                                                          blob=blobname)
        filename = blobname.split("/")[-1]
        localPath = os.path.join(tempfolder,filename)
        with open(localPath, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        localPath = os.path.join(tempfolder,filename)
        if foldername != str(blobindex // 10):
            print(foldername)
        foldername = str(blobindex // 10)
        splitblobname = blobname.split("/")
        splitblobname.insert(-1,foldername)
        newblobname = "/".join(splitblobname)

#        print(blobname,"--->",newblobname)

        tgtblob = blob_service_client.get_blob_client(
                container=container,blob = newblobname)
        with open(localPath, "rb") as data:
            tgtblob.upload_blob(data)

        blob_client.delete_blob()

