

import os
import shutil

inpFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/DataTagging/Processed"
outFolder = "D:/Invoice Data Extraction/TAPP 3.0/DataTagging/all"

allInpFolders = os.listdir(inpFolder)

for fld in allInpFolders:
    inpPath = os.path.join(inpFolder,fld)
    allFiles = os.listdir(os.path.join(inpFolder,fld))
    for fil in allFiles:
        newFileName = fld + "_" + fil
        inpFilePath = os.path.join(inpPath,fil)
        outFilePath = os.path.join(outFolder,newFileName)
        shutil.copy(inpFilePath,outFilePath)

