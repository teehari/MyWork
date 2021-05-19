# -*- coding: utf-8 -*-
from azure.storage.blob import BlobServiceClient
#import os
from dateutil import tz
import json
import pandas as pd
import datetime

# export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
to_zone = tz.tzlocal()
print("To zone:", to_zone)
download_file_path = "temp.json"
rows = []

remFolders = ["Hari","Ganesh","Shankar","Amit","Leanda","Temp"]
connect_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
connect_str = "DefaultEndpointsProtocol=https;AccountName=invtagging;AccountKey=lqvTPxTThicqxNjGPLfKn4I0ksoKDg//xz4n5IYsMYyDxmUJGde5QZX85h8jqCXPJ1Jni6S1Bg6p8C8PMOou6Q==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object which will be used to create a container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client("tagging-phase-3")

#Get all the blobs from the container
blobs = container_client.list_blobs(name_starts_with="Lineitem_9")
blobs = container_client.list_blobs()
actualfilenames = {}
filestagged = {}
for ind,b in enumerate(blobs):
    if len(rows) % 1000 == 0:
        print(len(rows) // 1000)
    blobname = b["name"]
    blobarr = blobname.split("/")
    if len(blobarr) > 1:
        folder = blobarr[0]
        if folder not in remFolders:
            filename = blobarr[1]
            filewoextn = filename[:filename.find(".TIF")]
            actfilename = filewoextn.rstrip(filewoextn.split("_")[-1])
            actfilename = actfilename.rstrip("_")
            pageno = filewoextn.split("_")[-1]

            if folder not in actualfilenames.keys():
                actualfilenames[folder] = set([])
            actualfilenames[folder].add(actfilename)

            if ".labels.json" in b["name"]:
                row = {}
                row["Folder"] = folder
                row["Tagger Name"] = folder
                row["Actual File Name"] = actfilename
                row["page number"] = pageno
                creation_time = b["creation_time"].astimezone(to_zone)
                row["Creation Time"] = creation_time.date()
                last_modified = b["last_modified"].astimezone(to_zone)
                row["Last Modified"] = last_modified.date()

                blob_client = blob_service_client.get_blob_client(container=b["container"],
                    blob=b["name"])

                with open(download_file_path, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
    
                with open(download_file_path) as json_file:
                    data = json.load(json_file)
                    for labels in data["labels"]:
                        label_text = ""
                        for values in labels["value"]:
                            label_text = label_text + values["text"] + " "
                        row[labels["label"]] = label_text.strip()
                rows.append(row)
                if folder not in filestagged.keys():
                    filestagged[folder] = set([])
                filestagged[folder].add(actfilename)

DF = pd.DataFrame(rows)
cols = list(DF.columns.values)
knowncols = ["Folder","Tagger Name","Actual File Name","page number",
             "Creation Time","Last Modified","index"]
blankcols = list(set(cols) - set(knowncols))

folders = actualfilenames.keys()

for folder in folders:
    allfiles = actualfilenames[folder]
    if folder in filestagged.keys():
        taggedfiles = filestagged[folder]
    else:
        taggedfiles = set([])
    untaggedfiles = allfiles - taggedfiles
    for filename in untaggedfiles:
        row = {}
        row["Folder"] = folder
        row["Tagger Name"] = folder
        row["Actual File Name"] = filename
        row["page number"] = "0"
        row["Creation Time"] = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
        row["Last Modified"] = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
        for col in blankcols:
            row[col] = ""
        rows.append(row)


remFolders = []
connect_str = "DefaultEndpointsProtocol=https;AccountName=invtagging;AccountKey=lqvTPxTThicqxNjGPLfKn4I0ksoKDg//xz4n5IYsMYyDxmUJGde5QZX85h8jqCXPJ1Jni6S1Bg6p8C8PMOou6Q==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object which will be used to create a container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client("tagging-phase-2")

#Get all the blobs from the container
#blobs = container_client.list_blobs(name_starts_with="Lineitem_9")
blobs = container_client.list_blobs()
actualfilenames = {}
filestagged = {}
for ind,b in enumerate(blobs):
    if len(rows) % 1000 == 0:
        print(len(rows) // 1000)
    blobname = b["name"]
    blobarr = blobname.split("/")
    if len(blobarr) > 1:
        folder = blobarr[0]
        if folder not in remFolders:
            filename = blobarr[1]
            filewoextn = filename[:filename.find(".TIF")]
            actfilename = filewoextn.rstrip(filewoextn.split("_")[-1])
            actfilename = actfilename.rstrip("_")
            pageno = filewoextn.split("_")[-1]

            if folder not in actualfilenames.keys():
                actualfilenames[folder] = set([])
            actualfilenames[folder].add(actfilename)

            if ".labels.json" in b["name"]:
                row = {}
                row["Folder"] = folder
                row["Tagger Name"] = folder
                row["Actual File Name"] = actfilename
                row["page number"] = pageno
                creation_time = b["creation_time"].astimezone(to_zone)
                row["Creation Time"] = creation_time.date()
                last_modified = b["last_modified"].astimezone(to_zone)
                row["Last Modified"] = last_modified.date()

                blob_client = blob_service_client.get_blob_client(container=b["container"],
                    blob=b["name"])

                with open(download_file_path, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())

                with open(download_file_path) as json_file:
                    data = json.load(json_file)
                    for labels in data["labels"]:
                        label_text = ""
                        for values in labels["value"]:
                            label_text = label_text + values["text"] + " "
                        row[labels["label"]] = label_text.strip()
                rows.append(row)
                if folder not in filestagged.keys():
                    filestagged[folder] = set([])
                filestagged[folder].add(actfilename)

DF1 = pd.DataFrame(rows)
cols = list(DF1.columns.values)
knowncols = ["Folder","Tagger Name","Actual File Name","page number",
             "Creation Time","Last Modified"]
blankcols = list(set(cols) - set(knowncols))

folders = actualfilenames.keys()

for folder in folders:
    allfiles = actualfilenames[folder]
    if folder in filestagged.keys():
        taggedfiles = filestagged[folder]
    else:
        taggedfiles = set([])
    untaggedfiles = allfiles - taggedfiles
    for filename in untaggedfiles:
        row = {}
        row["Folder"] = folder
        row["Tagger Name"] = folder
        row["Actual File Name"] = filename
        row["page number"] = "0"
        row["Creation Time"] = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
        row["Last Modified"] = str(datetime.datetime.now().year) + "-" + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day)
        for col in blankcols:
            row[col] = ""
        rows.append(row)


DF1 = pd.DataFrame(rows)
DF1 = DF1.drop_duplicates(keep="first")

DF1 = DF1[DF1["Actual File Name"] != ""]

DF = DF.append(DF1).reset_index()

DF.to_excel("Tagging_Status_2_" + str(datetime.datetime.now().date()) + ".xlsx",
            index = False)



