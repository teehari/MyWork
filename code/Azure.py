## -*- coding: utf-8 -*-
#"""
#Created on Mon Feb 10 10:58:59 2020
#
#@author: Hari
#"""
#
############ Python Form Recognizer Labeled Async Train #############
import json
import time
from requests import post,get

# Endpoint URL
endpoint = r"https://invrecognition.cognitiveservices.azure.com"
post_url = endpoint + r"/formrecognizer/v2.0-preview/custom/models"
source = r"https://tapp2data.blob.core.windows.net/training?sp=racwdl&st=2020-02-10T05:16:37Z&se=2022-02-11T05:16:00Z&sv=2019-02-02&sr=c&sig=kFr%2B%2F7MdyAOubpmpt3eVDkAJmTGEZ3s9Vr2MqQ1zl%2Bk%3D"
prefix = "training"
includeSubFolders = False
useLabelFile = False

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '17af270fe68c41439b92acd85f7ff121',
}

body = {
    "source": source,
    "sourceFilter": {
        "prefix": prefix,
        "includeSubFolders": includeSubFolders
    },
    "useLabelFile": useLabelFile
}

try:
    resp = post(url = post_url, json = body, headers = headers)
    if resp.status_code != 201:
        print("POST model failed (%s):\n%s" % (resp.status_code, json.dumps(resp.json())))
        quit()
    print("POST model succeeded:\n%s" % resp.headers)
    get_url = resp.headers["location"]
except Exception as e:
    print("POST model failed:\n%s" % str(e))
    quit()

n_tries = 2
n_try = 0
wait_sec = 5
max_wait_sec = 60

while n_try < n_tries:
    try:
        resp = get(url = get_url, headers = headers)
        resp_json = resp.json()
        if resp.status_code != 200:
            print("GET model failed (%s):\n%s" % (resp.status_code, json.dumps(resp_json)))
            quit()
        model_status = resp_json["modelInfo"]["status"]
        if model_status == "ready":
            print("Training succeeded:\n%s" % json.dumps(resp_json))
            quit()
        if model_status == "invalid":
            print("Training failed. Model is invalid:\n%s" % json.dumps(resp_json))
            quit()
        # Training still running. Wait and retry.
        time.sleep(wait_sec)
        n_try += 1
        wait_sec = min(2*wait_sec, max_wait_sec)     
    except Exception as e:
        msg = "GET model failed:\n%s" % str(e)
        print(msg)
        quit()
print("Train operation did not complete within the allocated time.")



