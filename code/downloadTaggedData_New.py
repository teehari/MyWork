# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 20:39:13 2020

@author: Hari
"""

from azure.storage.blob import BlobServiceClient
import os

filenames = []
root = r"D:\azuretemp\backup_2506"
os.makedirs(root,exist_ok=True)
blobfolders = ["Review_1","Review_2","Review_3","Review_4","Review_5",
               "Review_6","Review_7","Review_8","Review_9","Review_10",
               "Review_11","Review_12","Review_13","Review_14","Review_15"]
blobfolders = ["Lineitem_Completed","Tagging_Completed_2"]
blobfolders = ["Review_9"]

namefilter = ""
container = "formatseperator"
connect_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
#print(connect_str)
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container)

for blobfolder in blobfolders:

    blobs = container_client.list_blobs(name_starts_with=blobfolder)

    for blob in blobs:
        if namefilter in blob.name.lower():
            sep = blob.name.split("/")
            filename = sep[-1]
            foldername = sep[0]
            folder = os.path.join(root,foldername)
            os.makedirs(folder,exist_ok = True)
            tmpfilename = filename.rstrip(filename[filename.find(".TIF"):])
            splitnames = tmpfilename.split("_")
            tmpfilename = "_".join(splitnames[:3])
            filenames.append(tmpfilename)
            if tmpfilename in filenames:
                blob_client = blob_service_client.get_blob_client(container=container,
                                                              blob=blob.name)
                outfilepath = os.path.join(folder,filename)
                with open(outfilepath, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())

