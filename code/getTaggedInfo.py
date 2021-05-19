# -*- coding: utf-8 -*-
from azure.storage.blob import BlobServiceClient
import os
from dateutil import tz
import json
import pandas as pd
import datetime

# export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
to_zone = tz.tzlocal()
print("To zone:", to_zone)
download_file_path = "temp.json"

taggers = ["Suma",
"Nowfal",
"Aniket",
"Krishna",
"Suraj",
"Srikanth",
"Karri",
"Pratheeksha",
"Dulasinarkani",
"Vikas",
"Manjunath",
"Pavani",
"Moulika",
"Sriram",
"Leanda2"]

connect_str = "DefaultEndpointsProtocol=https;AccountName=tapp2data;AccountKey=C38zpM1CfufDmqcelnI/VvjIUpB6Fyoj8QUtsKrFs4f7pAKCpzMFRClSOhJW1thKSOdZB7Jm3OWughlSKEsuxg==;EndpointSuffix=core.windows.net"
print(connect_str)

# Create the BlobServiceClient object which will be used to create a container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client("formatseperator")

rows = []
for name in taggers:
    print("****************", name, "*****************")
    blobs = container_client.list_blobs(name_starts_with=name)
    for b in blobs:
        if ".labels.json" in b["name"]:
            row = {}
            row["Tagger Name"] = name
            file_name = b["name"].replace(".labels.json", "")
            file_name = file_name.replace(name+"/", "")
            row["File Name"] = file_name

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
#            print(row)
            rows.append(row)

DF = pd.DataFrame(rows)
DF.to_csv("Tagging_Status_" + str(datetime.datetime.now().date()) + ".csv")






