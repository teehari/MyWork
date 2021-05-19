

import os
import cv2
import numpy as np
import traceback

tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 360)
maxBorder = 50



def obtain_line_cor(org,img):

        blur = cv2.medianBlur(img,3)
        thresh = 150

        #Binarization of image - Make it strictly black or white 0 or 255
        pre = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        cpy1 = org.copy()
        height = img.shape[0]
        width = img.shape[1]
        vlines = []
        hlines = []

        #Identify vertical lines
        for i in range(width):
            single = pre[:,i:i+1][:,0]

            if len(single) > 0:
                vLines1 = findZeroPattern(single)
                for line in vLines1:
                    if line[1] - line[0] >= thresh:
                        cv2.line(cpy1,(i,line[0]),(i,line[1]),(0,255,0))
                        rectangle = (i,line[0],i,line[1])
                        vlines.append(rectangle)

        #Identify horizontal lines
        for i in range(height):
            single = pre[i:i+1,:][0]
            if len(single) > 0:
                hLines1 = findZeroPattern(single)
                for line in hLines1:
                    if line[1] - line[0] >= thresh:
                        cv2.line(cpy1,(line[0],i),(line[1],i),(0,0,255))
                        rectangle = (line[0],i,line[1],i)
                        hlines.append(rectangle)

        #cv2.imwrite(r"C:\Users\Admin\Pictures\fin_blu.tiff",cpy1)

        return hlines, vlines

def top_bottom_words(direc,i,unk,right,left,hline,diff_m, word_m ,cor_m):

    diff=35
    word=''
    cor=()
    ### unk is top or bottom here

    for h in hline:
        #print(i,h,box)
        x1=h[0]
        y1=h[1]  ### same as 3
        x2=h[2]
        y2=h[3]

        #print(x1 ,x2 ,left, right)
        if abs(y2-unk) < diff and left > x1 and right < x2:
            if  abs(y2-unk) < diff:
                diff= abs(y2-unk)
                word= i
                cor= h
    if cor!=():
        print(direc,diff,word,"len",cor[2]-cor[0])#,cor[2],cor[0], cor)
        diff_m.append(diff)
        word_m.append(word)
        length.append(abs(cor[2]-cor[0]))

    return diff_m, word_m , length

def left_right_words(direc,i,unk,bottom,top,vline,diff_m, word_m ,cor_m):

    diff=70
    word=""
    cor=()

    for v in vline:  
        x1=v[0]
        y1=v[1]  ### same as 3
        x2=v[2]
        y2=v[3]

        if abs(x2-unk) < diff and top > y1 and bottom < y2:
            if  abs(x2-unk) < diff:
                diff= abs(x2-unk)
                word= i
                cor= v     
    if cor!=():
        print(direc,diff,word,"len",cor[3]-cor[1])#,cor[1],cor[3],cor)
        diff_m.append(diff)
        word_m.append(word)
        length.append(abs(cor[2]-cor[0]))

    return diff_m, word_m , length 


def findZeroPattern(vals):
    binaryVals = vals // 255
    arr1 = np.concatenate(([0],binaryVals))
    arr2 = np.concatenate((binaryVals,[0]))
    ptnVals = np.bitwise_and(arr1,arr2)[1:]

    iszero = np.concatenate(([0], np.equal(ptnVals, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

import json

####################### obatin the lines ###############################

fullpath = r"C:\Users\Admin\Downloads\DataTagging\DataTagging\Processed\Format_18\Doc_1838.TIFF"

hline=[]
vline=[]

diff_m= []
word_m= []
length= []

print(fullpath.split("\\")[-1])
images = cv2.imreadmulti(fullpath)[1]

for image in images:
    temp_path=r"C:\Users\Admin\Desktop\New folder (3)\line1_Doc_1602_1.TIFF"
    cv2.imwrite(temp_path,image)
        #os.path.join(r"C:\Users\Admin\Desktop\New folder (3)",fullpath.split("\\")[-1]),image)
    img =cv2.imread(temp_path,0)
    org= cv2.imread(temp_path)
    #     org = image
    #img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #img= cv2.imread(fullpath,0)
    hline_t, vline_t = obtain_line_cor(org,img)  ## not applending so gives the cordinates for the last page
    hline.append(hline_t)
    vline.append(vline_t)
    # break

import itertools
hline  = list(itertools.chain(*hline))  ## flattening 
vline  = list(itertools.chain(*vline))

###############################          after obtaining the lines obatin the word and box #################

file= open(r"C:\Users\Admin\Documents\azure_json_dump\ocrs\Shankar\SGI_Doc_1838.TIFF.ocr.json")

read= file.read()
file.close()
dumps = json.loads(read)

words_len= len(dumps["analyzeResult"]["readResults"][0]["lines"][0]["words"])
page_no = len(dumps["analyzeResult"]["readResults"])
boundingBox= dumps["analyzeResult"]["readResults"][0]["lines"][0]["words"][0]["boundingBox"]
text= dumps["analyzeResult"]["readResults"][0]["lines"][0]["words"][0]["text"]

word_cor={}

for page in range(len(dumps["analyzeResult"]["readResults"])):
    for line in range(len(dumps["analyzeResult"]["readResults"][page]["lines"])):
        for word in range(len(dumps["analyzeResult"]["readResults"][page]["lines"][line]["words"])):
             word_cor[dumps["analyzeResult"]["readResults"][page]["lines"][line]["words"][word]["text"]]=dumps["analyzeResult"]["readResults"][page]["lines"][line]["words"][word]["boundingBox"]

words= list(word_cor.keys())   ### obatins the word bounding box
bounding_box= list(word_cor.values())   ## obtains the word

for i,box in zip(words,bounding_box):
    diff=35   # 35 also fine
    word=""
    cor=()

    top=max(box[1],box[3])
    left = max(box[0],box[6])
    right = max(box[4],box[2])
    bottom= max(box[7],box[5])

    diff_m, word_m , length = top_bottom_words("left",i,top,right,left,hline,diff_m, word_m ,length)

    diff_m, word_m , length = top_bottom_words("bottom",i,bottom,right,left,hline,diff_m, word_m ,length)

    diff_m, word_m , length  =left_right_words("left",i,left,bottom,top,vline,diff_m, word_m ,length)

    diff_m, word_m , length  =left_right_words("right",i,right,bottom,top,vline,diff_m, word_m ,length)



