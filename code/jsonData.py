import csv


import requests, json
import pandas as pd
from pathlib import Path
from csv import writer
import datetime


myfile = Path('processed.csv')
myfile.touch(exist_ok=True)

print(datetime.datetime.now())


excelFilePath = "FinalOutput.xlsx"
multipleFilesFolderPath = "MultiData/"

# Opening JSON file
file = open('input.json', )

# returns JSON object as
# a dictionary
flags = json.load(file)

isMultipleFiles = flags['isMultipleFiles']

print(isMultipleFiles)

ipAddress = flags['ipAddress']

def getFileNameByDocId(docId):
        try:

            url = ipAddress+'/document/get/'+docId
            response = requests.get(url, headers = {"Content-Type": "application/json"})
            data = response.json()
            data = data['result']

            data = data['document']

            fileName = data['fileName']

            return fileName
        except:
            return 'NA'





url = ipAddress+'/document/rpa/list'
body = {"id": "api.document.rpa.list",
    "ver": "1.0",
    "params": {
        "msgid": ""
    },
    "request": {
        "filter": {
           "status": "REVIEW"
         }
     }}

body = json.dumps(body)
response = requests.post(url, body, headers = {"Content-Type": "application/json"})
response_json = response.json()
result = response_json['result']
documents = result['documents']

count = 1
for i in documents:
    outputData = i
    documentId = outputData['documentId']
    documentLine = outputData['documentLineItems']
    del outputData['documentLineItems']
    fileName = getFileNameByDocId(documentId)
    outputData['fileName'] = fileName

    for z in documentLine:
        z['fileName'] =  fileName
        z['documentId'] = documentId






    isFound = False
    with open("processed.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if (row[0] == documentId):
                print("Found")
                isFound = True

    if isFound:
        continue

    if isMultipleFiles=='True':

        df = pd.DataFrame(outputData, index=[1])
        df2 = pd.DataFrame(documentLine)


        fileName_column = df.pop('fileName')

        # insert column using insert(position,column_name,
        # first_column) function
        df.insert(1, 'fileName', fileName_column)

        isempty = False
        isempty = df2.empty

        if isempty:
            pass
        else:
            fileName_column = df2.pop('fileName')
            documentId_Column = df2.pop('documentId')
            df2.insert(1, 'fileName', fileName_column)
            df2.insert(2, 'documentId', documentId_Column)
            df2.to_csv(multipleFilesFolderPath + fileName + "_lineitems.csv")

        df.to_csv(multipleFilesFolderPath+fileName+".csv")

    else:
        if count == 1:
            df = pd.DataFrame(outputData, index=[count])
            df2 = pd.DataFrame(documentLine)
        else:
            df = df.append(outputData, ignore_index=True)
            df2 = df2.append(documentLine, ignore_index=True)

    count  = count+1

    List = [documentId,datetime.datetime.now()]

    with open('processed.csv', 'a', newline='') as f_object:

        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)

        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(List)

        # Close the file object
        f_object.close()
    #Temporary condition
    if count == 500:
       break;


#If multiple files dont execute below
if isMultipleFiles!='True':
    writer = pd.ExcelWriter(excelFilePath, engine='xlsxwriter')

    fileName_column = df.pop('fileName')

    # insert column using insert(position,column_name,
    # first_column) function
    df.insert(1, 'fileName', fileName_column)

    df.to_excel(writer, sheet_name='Header')

    fileName_column = df2.pop('fileName')
    documentId_Column = df2.pop('documentId')
    df2.insert(1, 'fileName', fileName_column)
    df2.insert(2, 'documentId', documentId_Column)

    df2.to_excel(writer, sheet_name='LineItems')
    writer.save()


#test
df.to_csv("test.csv")
df2.to_csv("line.csv")



