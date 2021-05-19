########### Python Form Recognizer Async Layout #############

import json
import time
from requests import get, post
import os

# Endpoint URL
endpoint = r"https://invrecognition.cognitiveservices.azure.com"
apim_key = "f761839e80d744ae95bcfa23a665690c"
post_url = endpoint + "/formrecognizer/v2.0-preview/Layout/analyze"
#source = r"d:\\Invoice Data Extraction\\forms\\1_Doc_3.pdf"

headers = {
    # Request headers
    'Content-Type': 'image/tiff',
    'Ocp-Apim-Subscription-Key': apim_key,
}

inpFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/all"
outFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/analyzelayoutop"

files = os.listdir(inpFolder)

for fil in files:

    source = os.path.join(inpFolder,fil)
    print(source)
    if not os.path.exists(os.path.join(outFolder,fil + ".ocr.json")):

        with open(source, "rb") as f:
            data_bytes = f.read()

        try:
            resp = post(url = post_url, data = data_bytes, headers = headers)
            if resp.status_code != 202:
                print("POST analyze failed:\n%s" % resp.text)
                quit()
            print("POST analyze succeeded:\n%s" % resp.headers)
            get_url = resp.headers["operation-location"]
        except Exception as e:
            print("POST analyze failed:\n%s" % str(e))

        n_tries = 10
        n_try = 0
        wait_sec = 6
        while n_try < n_tries:
            try:
                resp = get(url = get_url,
                           headers = {"Ocp-Apim-Subscription-Key": apim_key})
                resp_json = json.loads(resp.text)
                if resp.status_code != 200:
                    print("GET Layout results failed:\n%s" % resp_json)
                status = resp_json["status"]
                if status == "succeeded":
                    print("Layout Analysis succeeded:\n%s" % source)
                    json_text = json.dumps(resp_json)
                    with open(os.path.join(outFolder,fil + ".ocr.json"),"w") as f:
                        f.write(json_text)
                    f.close()
                if status == "failed":
                    print("Layout Analysis failed:\n%s" % resp_json)
                # Analysis still running. Wait and retry.
                time.sleep(wait_sec)
                n_try += 1     
            except Exception as e:
                msg = "GET analyze results failed:\n%s" % str(e)
                print(msg)
#                quit()

