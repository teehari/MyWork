# -*- coding: utf-8 -*-
"""
Created on Tue May 19 19:48:30 2020

@author: Hari
"""

localtempfolder = r"d:\azuretemp"
source = "Raksha1"
target = "Noor"
limit = 1000

from azure.storage.blob import BlobServiceClient
import os
import pandas as pd

conn_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client("formatseperator")

#blobService = BlockBlobService(account_name=BLOB_ACCOUNT_NAME,
#                                       account_key=BLOB_ACCOUNT_KEY1)


container = "formatseperator"
#allBlobs = blobService.list_blobs(container)
allBlobs = container_client.list_blobs(name_starts_with=source)

localdir = os.path.join(localtempfolder,source)
os.makedirs(localdir,exist_ok=True)
localpaths = []
blobnames = []
actualfilenames = []
actualblobnames = []

for blob in allBlobs:
    blobPath = blob.name.split("/")
    if len(blobPath) == 3:
        blobdir = blobPath[1]
        blobname = blobPath[2]
    elif len(blobPath) == 2:
        blobdir = blobPath[0]
        blobname = blobPath[1]

    if blobdir.upper() == source.upper():
        localPath = os.path.join(localdir,blobname)
        _split = blobname.split("_")
        actualfilename = "_".join(_split[:len(_split) - 1])
        localpaths.append(localPath)
        blobnames.append(blobname)
        actualfilenames.append(actualfilename)
        actualblobnames.append(blob.name)

blobs = {}
blobs["localpath"] = localpaths
blobs["blobname"] = blobnames
blobs["filename"] = actualfilenames
blobs["blobname_act"] = actualblobnames

df = pd.DataFrame(blobs)

unqInvoice = list(df["filename"].unique())
cnt = 0

for invname in unqInvoice:
    files = list(df[df["filename"] == invname]["blobname"])
    lblFound = False
    for filename in files:
        if "labels.json" in filename:
            lblFound = True
            break
    if not lblFound:
        cnt += 1
        if cnt > limit:
            break
        pages = df[df["filename"] == invname]
        for indx, row in pages.iterrows():
            localPath = row["localpath"]
            blobname = row["blobname_act"]
            if not os.path.isfile(localPath):
                blob_client = blob_service_client.get_blob_client(container=container,
                                                                  blob=blobname)
                with open(localPath, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
                tgtblobname = target + "/" + row["blobname"]
                mimetype = ""
                if ".json" in tgtblobname:
                    mimetype = "application/json"
                else:
                    mimetype = "image/tiff"
                
                # Create a blob client using the local file name as the name for the blob
                tgtblob = blob_service_client.get_blob_client(
                        container=container,
                        blob=tgtblobname)
                with open(localPath, "rb") as data:
                    tgtblob.upload_blob(data)
                    
                blob_client.delete_blob()

localfiles = os.listdir(localdir)

if len(localfiles) > 0:
    for filename in localfiles:
        try:
            os.remove(os.path.join(localdir,filename))
        except:
            pass

