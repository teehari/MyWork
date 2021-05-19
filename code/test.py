# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:02:51 2020

@author: Hari
"""

import traceback
import os
from PIL import Image
import cv2
import numpy as np
import TAPPconfig as cfg
import shutil
import filecmp
import json
import requests
#import shutil
#Get all the blob stored details from config file
blobStoreProvider = cfg.getBlobStoreProvider()
if blobStoreProvider.lower().strip() == "azure":
    from azure.storage.blob import BlockBlobService
    from azure.storage.blob import ContentSettings

BLOB_ACCOUNT_NAME,BLOB_ACCOUNT_KEY1 = cfg.blobStoreDetails()

#get folder names
temp = cfg.getTemp()
from ghostscript import Ghostscript as GS
#Get GhostScript executable. The executable path should be added to system parameters.
#In windows it would be "PATH" environmental variable
ghostExecutable = cfg.getGhostPath()
ghostPause = cfg.getGhostPause()
ghostDevice = cfg.getGhostTiffDvc()
ghostDownScale = cfg.getGhostTiffDownScale()
ghostDownScaleFactor = cfg.getGhostTiffDownScaleFactor()
ghostQuit = cfg.getGhostQuit()
ghostCommandNoPause = cfg.getGhostCommandNoPause()
ghostCommandDsf = cfg.getGhostCommandDsf()
ghostCommandQuit = cfg.getGhostCommandQuit()
ghostCommandOut = cfg.getGhostCommandOut()
ghostCommandForce = cfg.getGhostCommandForce()
rootFolderPath = cfg.getRootFolderPath()

#Get mimetype and extensions
mimeTiff = cfg.getMimeTiff()
mimePdf = cfg.getMimePdf()
mimePng = cfg.getMimePng()
mimeJson = cfg.getMimeJson()
mimeXml = cfg.getMimeXml()
extnTiff = cfg.getExtnTiff()
extnPdf = cfg.getExtnPdf()
extnTxt = cfg.getExtnTxt()
extnJson = cfg.getExtnJson()
#Get the server URL to update doc status, doc results, etc.,
uiServerUrl = cfg.getUIServer()
docUpdUrl = cfg.getDocUpdURL()
docResCrtUrl = cfg.getDocResCrtURL()
docGetUrl = cfg.getDocGetURL()
vendorGetUrl = cfg.getVendorGetURL()
#Use GhostScript to convert PDF to tiff image
def convertPDFToTiff(src,dst):
    try:
        args = []
        bDst = dst.encode('utf-8')
        bSrc = src.encode('utf-8')
        args.append(b'' + ghostExecutable.encode('utf-8'))
        args.append(b'' + ghostDevice.encode('utf-8'))
        if ghostPause == 1:
            noPause = b"" + ghostCommandNoPause.encode('utf-8')
            args.append(noPause)
        if ghostDownScale == 1:
            args.append(b"" + ghostCommandDsf.encode('utf-8') + str(ghostDownScaleFactor).encode('utf-8'))
        args.append(b'' + ghostCommandOut.encode('utf-8'))
        args.append(b'' + bDst)
        args.append(b'' + bSrc)
        if ghostQuit == 1:
            args.append(b'' + ghostCommandForce.encode('utf-8'))
            args.append(b'' + ghostCommandQuit.encode('utf-8'))

        g = GS(*args)
        g.exit()
    except Exception as e:
        print(traceback.print_exc(),e)
        return False
    return True

#Download a single file from Blob store.
#This implementation will change using Azure blob container service
def downloadFromBlobStore(fileURI, localPath):
    try:
        blobService = BlockBlobService(account_name=BLOB_ACCOUNT_NAME,
                                       account_key=BLOB_ACCOUNT_KEY1)
        splitURI = fileURI.split("/")
        fileName = splitURI[len(splitURI) - 1]
        splitURI.pop(len(splitURI) - 1)
        container = "/".join([name for name in splitURI if name != ""])
        blobService.get_blob_to_path(container, fileName, localPath)
        return True
    except Exception as e:
        print(traceback.print_exc(),e)
        return False

#Upload a file to a blob store. This is specific to Azure blob storage
def uploadToBlobStore(filePath, container, fileName, mimeType):
    #Upload to Blob store
    try:
        blobService = BlockBlobService(account_name=BLOB_ACCOUNT_NAME,
                                       account_key=BLOB_ACCOUNT_KEY1)
        blobService.create_blob_from_path(container,fileName,filePath,
                                          content_settings=ContentSettings(content_type=mimeType))
        return True,container + "/" + fileName
    except Exception as e:
        print(traceback.print_exc(),e)
        return False, None

#Copy files from a source location to target location
def copyFile(srcPath,destPath):
    try:
        shutil.copy(srcPath,destPath)
        return True
    except Exception as e:
        print(traceback.print_exc(),e)
        return False

#Copy all the files from a folder to a target folder
def copyFolder(srcFolder, tgtFolder):

    try:
        shutil.rmtree(tgtFolder,ignore_errors = True)
        shutil.copytree(srcFolder,tgtFolder)
        return True
    except Exception as e:
        print(traceback.print_exc(),e)
        return False

#Delete all contents from a folder
def deleteFolderContents(inpFolder):
    try:
        for filename in os.listdir(inpFolder):
            file_path = os.path.join(inpFolder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(traceback.print_exc())
                return False
        return True
    except Exception as e:
        print(traceback.print_exc(),e)
        return False

#Download all files from a container.
#This implementation will change using Azure blob container service
def downloadAllFromContainer(container, localFolder):
    tempFolder = os.path.join(localFolder,temp)

    try:
        os.makedirs(tempFolder,exist_ok = True)
        #Delete from temp folder if any files are present
        d = deleteFolderContents(tempFolder)
        blobService = BlockBlobService(account_name=BLOB_ACCOUNT_NAME,
                                       account_key=BLOB_ACCOUNT_KEY1)
        allBlobs = blobService.list_blobs(container)
        for blob in allBlobs:
            localPath = os.path.join(tempFolder,blob.name)
            blobService.get_blob_to_path(container, blob.name,
                                         localPath)
            actualPath = os.path.join(localFolder,blob.name)
            if os.path.isfile(actualPath):
                same = filecmp.cmp(actualPath,localPath)
                if not same:
                    shutil.move(localPath,actualPath)
                else:
                    os.remove(localPath)
            else:
                shutil.move(localPath,actualPath)
        return True
    except Exception as e:
        print(traceback.print_exc(),e)
        return False
    finally:
        if os.path.isdir(tempFolder):
            try:
                shutil.rmtree(tempFolder)
            except:
                pass

#Identify file extn, filename, folder location
def getFileInfo(filePath):
    try:
        fileInfo = {}
        if os.path.isfile(filePath):
            fileParts = os.path.split(filePath)
            fileInfo["fullPath"] = filePath
            fileInfo["folderLoc"] = fileParts[0]
            fileInfo["filenameExtn"] = fileParts[1]
            fileInfo["filenameWoExtn"] = os.path.splitext(fileParts[1])[0]
            fileInfo["extn"] = os.path.splitext(fileParts[1])[1]
            stats = os.stat(filePath)
            fileInfo["createdTime"] = stats.st_ctime
            fileInfo["modifiedTime"] = stats.st_mtime
            fileInfo["size"] = stats.st_size
            return fileInfo
        else:
            return None
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

#Get Image Dimension, Quality Info
def getImageInfo(imgPath):
    try:
        imageInfo = {}
        if os.path.isfile(imgPath):
            imgb = Image.open(imgPath,mode = 'r')
            if "dpi" in imgb.info.keys():
                qual = imgb.info["dpi"]
                hDpi = int(qual[0])
                vDpi = int(qual[1])
                compression = imgb.info["compression"]
            else:
                hDpi = -1
                vDpi = -1
                compression = "none"
            imgb = None
            imageInfo["hDPI"] = hDpi
            imageInfo["vDPI"] = vDpi
            imageInfo["aDPI"] = (hDpi + vDpi) // 2
            imageInfo["compression"] = compression
            img = cv2.imread(imgPath, cv2.IMREAD_GRAYSCALE)
            size = img.shape
            h = size[0]
            w = size[1]
            imageInfo["height"] = h
            imageInfo["width"] = w
            img = None
            return imageInfo
        else:
            return None
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

#detect boundaries in an image
def applyCanny(img, sigma=0.33):
    try:
        v = np.median(img)
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        return cv2.Canny(img, lower, upper)
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

#Detect regions in an image
def detectRegions(img):
    try:
        mser = cv2.MSER_create()
        regions, bboxes = mser.detectRegions(img)
        return regions, bboxes
    except Exception as e:
        print(traceback.print_exc(),e)
        return None, None

def updateDocumentApi(documentId,docInfo, callbackUrl):

    try:
        updUrl = callbackUrl + "/" + docUpdUrl + "/" + documentId
        data = json.dumps(docInfo)
        headers = {}
        headers["Content-Type"] = mimeJson

        r = requests.post(updUrl, data = data, headers = headers)
        if r.status_code == 200:
            print("Success")
            return True
        else:
            print(r.status_code)
            return False
    except Exception as e:
        print(traceback.print_exc(),e)
        return False

def getDocumentApi(documentId, callbackUrl):

    getUrl = callbackUrl + "/" + docGetUrl + "/" + documentId
    try:
        headers = {}
        headers["REQUEST"] = mimeJson
        r = requests.get(getUrl, headers = headers)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            return None
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

def getVendorApi(vendorId, callbackUrl):

    getUrl = callbackUrl + "/" + vendorGetUrl + "/" + vendorId
    try:
        headers = {}
        headers["REQUEST"] = mimeJson
        r = requests.get(getUrl, headers = headers)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            return None
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

def createDocumentResultsApi(documentId, docResultsInfo, callbackUrl):

    try:
        url = callbackUrl + "/" + docResCrtUrl
        data = json.dumps(docResultsInfo)
        headers = {}
        headers["Content-Type"] = mimeJson

        r = requests.post(url, data = data, headers = headers)
        if r.status_code == 200:
            print("Success")
            return True
        else:
            return False
    except Exception as e:
        print(traceback.print_exc(),e)
        return False

def pathMerger(tailPath,relativeFolder,storageType):
    if storageType== "BLOB":
        return tailPath
    elif storageType == "FOLDER":
        return os.path.join(rootFolderPath,relativeFolder,tailPath.replace(rootFolderPath,"").lstrip("/").lstrip("\\\\").lstrip("\\"))
    else:
        return tailPath

def getVendorList(callbackUrl):

    try:
        getVendorListAPI = cfg.getVendorListAPI()
        vendorListUrl = callbackUrl + "/" + getVendorListAPI
        print(vendorListUrl)
        docInfo = {
                    "id": "api.vendor.list",
                       "params": {
                           "msgid": ""
                       },
                       "request": {
                        "token":"",
                            "filter": {
                            }
                    }
                    }
        print(docInfo)
        data = json.dumps(docInfo)
        headers = {}
        headers["Content-Type"] = mimeJson

        r = requests.post(vendorListUrl, data = data, headers = headers)
        if r.status_code == 200:
            print("Success")
            response = r.json()
#            print(response)

            return response
        else:
            print(r.status_code)
            return None
    except Exception as e:
        print(traceback.print_exc(),e)
        return None

knownInvDesc = {}
def getVendorSamples():
    try:
        vendorApiResult = getVendorList("http://104.211.177.15:8080")
        vendorResult = vendorApiResult["result"]
        allVendors = vendorResult["documents"]
        for vendor in allVendors:
            if "sampleInvoices" in vendor.keys():
                vendorId = vendor["vendorId"]
                compareFile = vendor["sampleInvoices"]
                orb = cv2.ORB_create()
                try:
                    img = cv2.imread(compareFile,0)
                    kp, desc = orb.detectAndCompute(img, None)
                    knownInvDesc[vendorId] = desc
                except:
                    pass
        print(knownInvDesc.keys())
        return True
    except Exception as e:
        print(traceback.print_exc(),e)
        return False
