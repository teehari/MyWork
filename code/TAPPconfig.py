# -*- coding: utf-8 -*-

import json
import os

#Load configuration
with open("config.json") as config_file:
    configdata = json.load(config_file)

config_file.close()

def getConfigData():
    return configdata

def getBlobStoreProvider():
    blobStoreProvider = configdata["BLOB_STORAGE_PROVIDER"]
    return blobStoreProvider

def blobStoreDetails():
    accountName = configdata["BLOB_ACCOUNT_NAME"]
    accountKey = configdata["BLOB_ACCOUNT_KEY1"]
    return accountName, accountKey

def getFolder(name):
    folder = configdata[name]
    os.makedirs(folder, exist_ok = True)
    return folder

def getDocMapFolder():
    return getFolder("DOCUMENT_TEMPLATE_MAPPING_FOLDER")

def getTiffFolder():
    return getFolder("TIFF_CONVERTED_FOLDER")

def getPngFolder():
    return getFolder("PNG_CONVERTED_FOLDER")

def getPreProcAsyncFolder():
    return getFolder("ASYNC_PROC_START_FOLDER")

def getCompareTemplateFolder():
    return getFolder("COMPARE_TEMPLATES_FOLDER")

def getSplitFolder():
    return getFolder("SPLIT_FOLDER")

def getDownloadFolder():
    return getFolder("DOWNLOAD_FOLDER")

def getPreProcAsyncInprogFolder():
    return getFolder("ASYNC_PROC_INPROG_FOLDER")

def getAbbyyResultXmlToJsonMap():
    return getFolder("ABBYY_RESULTXML_JSON_MAP")

def getExtractionTempFolder():
    return getFolder("EXTRACTION_TEMP")

def getDeskewFileSuffix():
    return configdata["DESKEW_FILE_SFX"]

def getCroppedFileSuffix():
    return configdata["CROPPED_FILE_SFX"]

def getMultiPageFileSuffix():
    return configdata["MULTIPAGE_FILE_SFX"]

def getEnhancedFileSuffix():
    return configdata["ENHANCED_FILE_SFX"]

def getPreprocessedFileSuffix():
    return configdata["PREPROCESSED_FIL_SFX"]

def getGhostPath():
    return configdata["GHOST_SCRIPT_EXE"]

def getGhostTiffDvc():
    return configdata["GHOST_TIFF_DEVICE"]

def getGhostPause():
    return configdata["GHOST_TIFF_PAUSE"]

def getGhostTiffDownScale():
    return configdata["GHOST_DOWN_SCALE"]

def getGhostTiffDownScaleFactor():
    return configdata["GHOST_DOWN_SCALE_FACTOR"]

def getGhostQuit():
    return configdata["GHOST_QUIT"]

def getGhostCommandNoPause():
    return configdata["GHOST_COMMAND_NOPAUSE"]

def getGhostCommandDsf():
    return configdata["GHOST_COMMAND_DSF"]

def getGhostCommandQuit():
    return configdata["GHOST_COMMAND_QUIT"]

def getGhostCommandOut():
    return configdata["GHOST_COMMAND_OUT"]

def getGhostCommandForce():
    return configdata["GHOST_COMMAND_FORCE"]

def getUIServer():
    return configdata["UI_SERVER"]

def getDocUpdURL():
    return configdata["DOCUMENT_UPDATE_URL"]

def getDocResUpdURL():
    return configdata["DOCUMENT_RESULT_UPDATE_URL"]

def getDocResCrtURL():
    return configdata["DOCUMENT_RESULT_CREATE_URL"]

def getDocGetURL():
    return configdata["DOCUMENT_GET_URL"]

def getVendorGetURL():
    return configdata["VENDOR_GET_URL"]

def getAbbyyHotFolder():
    return configdata["ABBYY_HOT_FOLDER"]

def getAbbyyExportFolder():
    return configdata["ABBYY_EXPORT_FOLDER"]

def getAbbyyUnknownFolder():
    return configdata["ABBYY_UNKNOWN_FOLDER"]

def getCropBorder():
    return configdata["CROP_BORDER"]

def getImgSimFlannMtchDist():
    return configdata["IMAGE_SIM_FLANN_MATCH_DIST"]

def getImgSimFlannMtchThresh():
    return configdata["IMAGE_SIM_FLANN_MATCH_THRESH"]

def getExtractionEngine():
    return configdata["EXTRACTION_ENGINE"]

def getDocumentType():
    return configdata["DOCUMENT_TYPE"]

def getStorageType():
    return configdata["STORAGE_TYPE"]

def getBlobStoreImport():
    return configdata["BLOB_FOLDER_IMPORT"]

def getBlobStorePreproc():
    return configdata["BLOB_FOLDER_PREPROC"]

def getBlobStoreExport():
    return configdata["BLOB_FOLDER_EXPORT"]

def getBlobStoreCompareTemplate():
    return configdata["BLOB_FOLDER_COMPARE_TEMPLATE"]

def getBlobStoreTempResMap():
    return configdata["BLOB_FOLDER_TEMPLATE_RESULT_MAP"]

def getFolderImport():
    return configdata["FOLDER_IMPORT"]

def getFolderPreproc():
    return configdata["FOLDER_PREPROC"]

def getFolderExport():
    return configdata["FOLDER_EXPORT"]

def getFolderCompareTemplate():
    return configdata["FOLDER_COMPARE_TEMPLATE"]

def getFolderTempResMap():
    return configdata["FOLDER_RESULT_MAP"]

def getFolderSampleInvoice():
    return configdata["FOLDER_SAMPLE_INVOICE"]

def getFolderExtraction():
    return configdata["FOLDER_ABBYY_RESULT"]

def getRootFolderPath():
    return configdata["ROOT_FOLDER"]

def getSystemUser():
    return configdata["SYSTEM_USER"]

def getTappVersion():
    return configdata["TAPP_VERSION"]

def getDocUpdApi():
    return configdata["DOCUMENT_UPDATE_API_ID"]

def getDocResAddApi():
    return configdata["DOCUMENT_RESULT_ADD_API_ID"]

def getStatusPreprocInProg():
    return configdata["STATUS_PREPROC_INPROGRESS"]

def getStatusReadyExtract():
    return configdata["STATUS_READY_FOR_EXTRACTION"]

def getStatusExtractInProg():
    return configdata["STATUS_EXTRACTION_INPROGRESS"]

def getStatusExtractDone():
    return configdata["STATUS_EXTRACTION_DONE"]

def getStatusFailed():
    return configdata["STATUS_FAILED"]

def getParamStatusSuccess():
    return configdata["PARAM_STATUS_SUCCESS"]

def getParamStatusFailed():
    return configdata["PARAM_STATUS_FAILED"]

def getErrcodeError():
    return configdata["ERRORCODE_ERROR"]

def getErrcodeExtResUpdFail():
    return configdata["ERRORCODE_EXT_RESULT_UPDATE_FAILED"]

def getErrcodeExtTpl404():
    return configdata["ERRORCODE_EXT_TEMPLATE_NOT_FOUND"]

def getErrcodePreprocDocNotAcc():
    return configdata["ERRORCODE_PREPROC_DOC_NOT_ACCEPTED"]

def getErrcodePreprocFail():
    return configdata["ERRORCODE_PREPROC_FAILED"]

def getErrcodePreprocDocTpl404():
    return configdata["ERRORCODE_PREPROC_DOC_TPL_404"]

def getErrcodePreprocImgEnhFail():
    return configdata["ERRORCODE_PREPROC_IMG_ENH_FAILED"]

def getErrmsgExtractInitFail():
    return configdata["ERRORMSG_EXT_INITIATION_FAILED"]

def getErrmsgExtractResNotUpd():
    return configdata["ERRORMSG_EXT_RESULTS_NOT_UPDATED"]

def getErrmsgExtractTpl404():
    return configdata["ERRORMSG_EXT_NO_TEMPLATE_FOUND"]

def getErrmsgPreprocFileNotDownload():
    return configdata["ERRORMSG_PREPROC_FILE_NOT_DOWNLOADED"]

def getErrmsgPreprocNotValidInv():
    return configdata["ERRORMSG_PREPROC_NOT_VALID_INVOICE"]

def getErrmsgPreprocTiffConv():
    return configdata["ERRORMSG_PREPROC_TIFF_FILE_CONVERT"]

def getErrmsgPreprocFail():
    return configdata["ERRORMSG_PREPROC_FAILED"]

def getErrmsgPreprocNomatchInv():
    return configdata["ERRORMSG_PREPROC_NOMATCH_INVOICE"]

def getErrmsgPreprocImgEnhFail():
    return configdata["ERRORMSG_PREPROC_FAILED_IMG_ENHANCEMENT"]

def getStatusmsgPreprocCompleted():
    return configdata["STATUSMSG_PREPROC_COMPLETED"]

def getStatusmsgPreprocAccepted():
    return configdata["STATUSMSG_PREPROC_ACCEPTED"]

def getStatusmsgExtractSuccess():
    return configdata["STATUSMSG_EXTRACTION_SUCCESS"]

def getStatusmsgExtractInitated():
    return configdata["STATUSMSG_EXTRACTION_INITIATED"]

def getTappMlProbThreshold():
    return configdata["TAPP_ML_PROB_THRESHOLD"]

def getMultiPageTiffCompress():
    return configdata["MULTIPAGE_TIFF_COMPRESSION"]

def getMimeTiff():
    return configdata["MIMETYPE_TIFF"]

def getMimeTif():
    return configdata["MIMETYPE_TIF"]

def getMimePng():
    return configdata["MIMETYPE_PNG"]

def getMimePdf():
    return configdata["MIMETYPE_PDF"]

def getMimeJson():
    return configdata["MIMETYPE_JSON"]

def getMimeXml():
    return configdata["MIMETYPE_XML"]

def getExtnTiff():
    return configdata["EXTN_TIFF"]

def getExtnTif():
    return configdata["EXTN_TIF"]

def getExtnPdf():
    return configdata["EXTN_PDF"]

def getExtnTxt():
    return configdata["EXTN_TXT"]

def getExtnJson():
    return configdata["EXTN_JSON"]

def getTemp():
    return configdata["TEMP_FOLDER"]

def getNoPageToCompare():
    return configdata["NO_PAGES_TO_COMPARE"]

def getStagePreproc():
    return configdata["STAGE_PREPROC"]

def getStageExtract():
    return configdata["STAGE_EXTRACT"]

def getConstCallbackUrl():
    return configdata["CONST_CALLBACKURL"]

def getXmlRetryCount():
    return configdata["XML_RETRY_COUNT"]

def getExtractionPort():
    return configdata["EXTRACTION_PORT"]

def getPreprocPort():
    return configdata["PREPROC_PORT"]

def getPreprocSync():
    return configdata["PREPROC_SYNC"]

def getPreprocParallel():
    return configdata["PREPROC_PARALLEL"]

def getVendorListAPI():
    return configdata["GET_VENDOR_API"]
