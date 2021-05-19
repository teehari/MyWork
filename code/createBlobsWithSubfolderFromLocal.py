# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 10:51:11 2020

@author: Hari
"""

from azure.storage.blob import BlobServiceClient
import os
import re

conn_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container = "formatseperator"

localtempfolder = r"d:\azuretemp\backup_2506\Review_4"

files = os.listdir(localtempfolder)

basefiles = set([])

for fil in files:
    splitblobname = re.split("_[0-9]{1,3}.TIF",fil)
    basefilename = splitblobname[0]
    basefiles.add(basefilename)

for ind,basefile in enumerate(basefiles):
    matchingfiles = [filename for filename in files if basefile in filename]
    newfolder = str((ind // 10) + 1)
    blobfolder = "Review_4/" + newfolder + "/"
    for matchfile in matchingfiles:
        blobname = blobfolder + matchfile
        tgtblob = blob_service_client.get_blob_client(
                container=container,blob = blobname)

        localPath = os.path.join(localtempfolder,matchfile)
        with open(localPath, "rb") as data:
            tgtblob.upload_blob(data)

