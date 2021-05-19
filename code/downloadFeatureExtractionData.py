# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 20:39:13 2020

@author: Hari
"""

from azure.storage.blob import BlobServiceClient
import os
from dateutil import tz
import json
import pandas as pd
import datetime

root = r"D:\Invoice Data Extraction\TAPP 3.0\Sample Model"
container = "tapp-data"
name = "COPY_DATASET_INVOICE_PAGES_OT_PHASE1_FEATURE_1/DIAGIO/"
connect_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
#print(connect_str)
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container)
blobs = container_client.list_blobs(name_starts_with=name)

for blob in blobs:
    blob_client = blob_service_client.get_blob_client(container=container,
                                                      blob=blob.name)
    filename = blob.name.replace(name,"")
    outfilepath = os.path.join(root,filename)
    with open(outfilepath, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())


