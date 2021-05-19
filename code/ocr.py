# -*- coding: utf-8 -*-
import json
import time
from requests import get, post
import os
from pdf2image import convert_from_path
import cv2
import pandas as pd
import pytesseract
from pytesseract import Output
import numpy as np

# Endpoint URL
endpoint = r"https://invrecognition.cognitiveservices.azure.com"
apim_key = "f761839e80d744ae95bcfa23a665690c"
post_url = endpoint + "/formrecognizer/v2.1-preview.2/Layout/analyze"
ocr_out_folder = "temp"
mime_type = "image/tiff"

headers = {
    # Request headers
    'Content-Type': mime_type,
    'Ocp-Apim-Subscription-Key': apim_key,
}

def get_analyseLayout(imgpath):

    status = False

    print("Start OCR For file:",imgpath)
    filename = os.path.basename(imgpath)
    ocr_out_path = os.path.join(ocr_out_folder,filename + ".azure.json")

    if os.path.exists(ocr_out_path):
        return True, ocr_out_path

    with open(imgpath, "rb") as f:
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
        return status, ocr_out_path

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
                print("Layout Analysis succeeded:\n%s" % imgpath)
                json_text = json.dumps(resp_json)
                with open(ocr_out_path,"w") as f:
                    f.write(json_text)
                f.close()
                status = True
                break
            if status == "failed":
                print("Layout Analysis failed:\n%s" % resp_json)
            # Analysis still running. Wait and retry.
            time.sleep(wait_sec)
            n_try += 1
        except Exception as e:
            msg = "GET analyze results failed:\n%s" % str(e)
            print("ERROR:",msg)

    return status, ocr_out_path

def get_JPG_file(in_path):
    """
    """
    list_direct = [x[0] for x in os.walk(in_path)]
    list_files = [x[2] for x in os.walk(in_path)]
    assert len(list_direct) == len(list_files), "Error in reading files and folder structure in the path"

    list_dir_ = []
    list_files_ = []
    for index, dir_ in enumerate(list_direct):
        jpg_file = []
        files = list_files[index]
        if ".DS_Store" in files:
            files.remove(".DS_Store")
        for f in files:
            if (f.count('.') == 1) and (".JPG" in f.upper()):
                # TIFF File found
                jpg_file.append(f)
        if len(jpg_file) > 0:
            list_dir_.append(dir_)
            list_files_.append(jpg_file)

    path_files = []
    for i in range(0, len(list_dir_)):
        dir_ = list_dir_[i]
        files = list_files_[i]
        for f in files:
            path_files.append(os.path.join(dir_, f))

    return path_files





def read_and_enhance_image(image_path):
    """

    :param image_path:
    :return:
    """
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    kernel_sharpening = np.array([[0, -1, 0],
                                  [-1, 5, -1],
                                  [0, -1, 0]])

    image = cv2.filter2D(image, -1, kernel_sharpening)

    image = cv2.threshold(image, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return image


def get_ocr_output(image_path):
    """

    :param image_path:
    :return:
    """

    image = read_and_enhance_image((image_path))
    try:
        df = pd.DataFrame(pytesseract.image_to_data(image,
                                                    output_type=Output.DICT,
                                                    lang='eng', config='--psm 6'))
        df['file_name'] = image_path
        df['page_name'] = image_path
        # Extract relevant features
        df['right'] = df['left'] + df['width']
        df['bottom'] = df['top'] + df['height']
        df = df.loc[~(df['text'].isna())].reset_index(drop=True)
        df = df.loc[~(df['text'].isnull())].reset_index(drop=True)
        filename = os.path.basename(image_path)
        ocr_out_path = os.path.join(ocr_out_folder,filename + ".tess.json")
        df.to_json(ocr_out_path)
        return df
    except Exception as e:
        print("Exception in get_ocr_output")



in_path = "temp"
path =  get_JPG_file(in_path)


for file in path:
    get_ocr_output(file)
    get_analyseLayout(file)
