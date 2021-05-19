# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 21:38:21 2020

@author: Hari
"""

from azure.storage.blob import BlobServiceClient
#import os
from dateutil import tz
import json
import pandas as pd
import datetime
import time
import os

# export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
to_zone = tz.tzlocal()
print("To zone:", to_zone)
#download_file_path = "temp.json"
rows = []
outdir = r"D:\azuretemp"

connect_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object which will be used to create a container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client("formatseperator")

#Get all the blobs from the container
blobs = container_client.list_blobs(name_starts_with="Review_14")

#Define Label list - from labels.json
labels = set([])

#Define fields from fields.json
fields = set([])

for blobind, b in enumerate(blobs):
    if ".labels.json" in b["name"].lower():
        blob_client = blob_service_client.get_blob_client(container=b["container"],
                                                          blob=b["name"])
        tmp = str(time.time()) + ".json"
        download_file_path = os.path.join(outdir,tmp)
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        with open(download_file_path) as json_file:
            data = json.load(json_file)
        os.remove(download_file_path)
        allLabels = data["labels"]
        for labelObj in allLabels:
            labels.add(labelObj["label"])
    if "fields.json" in b["name"].lower():
        blob_client = blob_service_client.get_blob_client(container=b["container"],
                                                          blob=b["name"])
        tmp = str(time.time()) + ".json"
        download_file_path = os.path.join(outdir,tmp)
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        with open(download_file_path) as json_file:
            data = json.load(json_file)
        os.remove(download_file_path)
        allFields = data["fields"]
        for fieldObj in allFields:
            fields.add(fieldObj["fieldKey"])
            
print(labels - fields)
