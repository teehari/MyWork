# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 21:24:25 2020

@author: Hari
"""

import boto3
import os
from PIL import Image
import json
import time
import img2pdf as i2p
import guid

bucketName = "textract-console-us-east-2-dca76d68-af00-4a91-9b6a-471e7f8ed46d"

textract = boto3.client('textract',region_name='us-east-2',
                        aws_access_key_id='AKIAXBSSQ632EYBDP6RB',
                        aws_secret_access_key='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')

s3 = boto3.client('s3',region_name='us-east-2',
                  aws_access_key_id='AKIAXBSSQ632EYBDP6RB',
                  aws_secret_access_key='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')

#inpFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/Processed"
inpFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/Output"
opFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/AWS_OP"
#pdfFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/Output_pdf"
pdfFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/Output_pdf"

for root, subFolder, fileNames in os.walk(inpFolder):
    for fileName in fileNames:
        folderName = os.path.split(root)[1]
        opPath = os.path.join(pdfFolder,folderName)
        os.makedirs(opPath,exist_ok=True)
        inpFilePath = os.path.join(root,fileName)
        extn = os.path.splitext(fileName)[1]
        extn = extn.upper()
        fileNameWoExtn = extn = os.path.splitext(fileName)[0]
#        opFileName = fileNameWoExtn + ".pdf"
        opFileName = fileNameWoExtn + ".jpg"
        outFilePath = os.path.join(opPath,opFileName)
        if not os.path.exists(outFilePath):
            im = Image.open(inpFilePath)
#            pdf_bytes = i2p.convert(im.filename)
#            f = open(outFilePath,"wb")
#            f.write(pdf_bytes)
#            im.close()
#            f.close()
            im.thumbnail(im.size)
            im.save(outFilePath,"JPEG")
            print("File being uploaded to S3", opFileName)
            t = time.time()
            response = s3.upload_file(outFilePath, bucketName, opFileName)
            print("File Uploaded to S3",time.time() - t)
            with open(outFilePath,'rb') as document:
                imageBytes = bytearray(document.read())
                # Call Amazon Textract
                print("Amazon Document Analysis Called")
                t = time.time()
#                response = textract.analyze_document(Document={'Bytes': imageBytes},
#                                                     FeatureTypes=["TABLES", "FORMS"])
                response = textract.start_document_analysis(ClientRequestToken=str(guid.guid.uuid4()),
                                                 DocumentLocation={
                                                         'S3Object':
                                                             {"Bucket":bucketName,
                                                              "Name":opFileName
                                                              }
                                                             },
                                                         FeatureTypes=["TABLES", "FORMS"],
                                                         JobTag="Invoice"
                                                         )
                responseCode = response["ResponseMetadata"]["HTTPStatusCode"]
                if responseCode == 200:
                    jobId = response["JobId"]

                    for i in range(1000):
                        getResponse = textract.get_document_analysis(JobId=jobId)
                        jobStatus = getResponse['JobStatus']
                        if jobStatus == "IN_PROGRESS":
                            time.sleep(5)
                        else:
                            print("Amazon Service returned",time.time() - t,
                                  fileName)
                            respObj = json.dumps(getResponse["Blocks"])
                            jsonFileName = fileNameWoExtn + ".json"
                            jsonPath = os.path.join(opFolder,folderName)
                            os.makedirs(jsonPath,exist_ok=True)
                            jsonOpPath = os.path.join(jsonPath,jsonFileName)
                            f = open(jsonOpPath,'w')
                            f.write(respObj)
                            f.close()
                            break

print("All Done")
# Call Amazon Textract
#response = textract.detect_document_text(
#    Document={
#        'S3Object': {
#            'Bucket': s3BucketName,
#            'Name': documentName
#        }
#    })

#response = textract.analyze_document(
#    Document={
#        'S3Object': {
#            'Bucket': s3BucketName,
#            'Name': documentName
#        }
#    },
#    FeatureTypes=["TABLES", "FORMS"])
#
