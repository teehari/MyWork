import pandas as pd
import os
import re


src = r"C:\Users\Admin\Desktop\Working\myFeatures"
# filepath = r"C:\Users\Admin\Desktop\Working\myFeatures\Doc_6_FEATURES.csv"


curreny_List = ["GBP","SGD","USD","EUR","EURO","pound","Pounds","Sterling","(GBP)","GBR","GB","Pounds.","KES","GBP-British","(EUR)","$","GBP:","ZAR","INR"]
UOM_List = ["db","DAY","Piece","EA","PCS","m","pc.","CYL","EACH","PC","LT","Pallets","Case","KG","Pallet","Lot","Hour","Lots","PCE","(EA)","PR","PRC","YR","unit","EUX","Units","User","License","STK","pes","PE","GFN","stk."]
country_List = ["Europe","England","UK","Columbus","US","Singapore","Hertfordshire","Stamford","Ireland","Milano","Devon","Oxon","Peruwelz","France","Nottingham","Canada","The Netherlands","South Glos","Gurugram","Manchester","Berkshire","Wereda","Peldanyszam","Draper","Buckinghamshire","Scotland","St Helens","New Yorl","London","East Sussex","Polaska","Myanmar","Japan","Middlesex","Ballygowan","Belgium","Boerne","Germany","Herts","Cambridge","United Kingdom","Esparreguera","Some rse t","Kent","India","Netherlands","Madrid","Amsterdam The Netherlands","South Africa","Alpharetta","Antrim","Nr Knutsford","Pretoria","Australia","Dalla","Italy","New York","United States of America","California","EDINBURGH","Great Britain","Brussels","Whybrow","Krakow","Uruguay","Leeds","New Bury","Washington","NSW","Brentford","Harlow","Switzerland","West Sussex","Hampshire","Surrey","Hong Kong","Middlesbrough","Glasgow","Cheshire","Essex","Koln","Twickenham","Warwick","Liverpool","Lancashire","Yorkshire","Sussex","Tamworth","Hamshipre","Westhoughton","Aldates","Britain","Brooklyn","Peebles","Darmstadt","Buckinghumshipre","Kulmbach","Estate York","Salford","Nertherland","Preston","Huntingdon","Warrington","Orlando","Berkshipre","Co.Louth","Pennsylvania","Bangkok","Runcorn","Stafforshipre","USA","Narthampton","Edingurgh","Wycombe","Penarth","Staffordshire","Swindon","Dublin","Netherland","BRISTOL","Dorset","Lincolnshipre","Brasil","Masku","Caerphilly","Aldershot","Wrexham","Birmingham","Durban","Slough","Pepper lane","Holywood","Denmark","Bolton","Shropshire","Albans","West Midlands","Hempstead","Cumbernauld","Kholin","West Yorkshire","Cheshipre","Derby","Kenya","Basingstoke","Northamptonshipre","Westfallca","Ethiopia","Korea","CA","Nevada","Chicago","Las vegas","NV","IND","AUS"]
keywordlist = ['invoice','inv','quantity','qty','item','po','number','no.','description','desc','payment','terms','net','days','due','date','dt','reference','vat','tax','total','unit','units','price','amount','amt','bill','ship','billing','shipping','address','payment','reference','value','unit','purchase','ref','uom','weight','wt','services','service','fee','charge','charges','gst','rate','currency','order','discount','subtotal','sub-total','ship','balance','code','period','bank','remittance','account','advice','customer']
noOfPuncs_list = ["noOfPuncs","countOfColon","countOfSemicolon","countOfHyphen","countOfComma","countOfPeriod"]

text_emb = []
rev_emb = []
shape_emb = []
for i in range(1,31):
    text_emb.append("emb_"+str(i))
    shape_emb.append("shape_"+str(i))
    rev_emb.append("rev_"+str(i))

foo = lambda x: pd.Series([i for i in x])
oof = lambda x: pd.Series([i for i in reversed(x)])

def isAlphaNumeric(text):
    return 1 if not(pd.isna(text)) and text.isalnum() else 0

def isAlpha(text):
    return 1 if not(pd.isna(text)) and str(text).isalpha() else 0

def isNumber(text):
    return 1 if  not(pd.isna(text)) and str(text).isdigit() else 0

def noOfPuncs(text):
    count = 0
    colon = 0
    semicolon = 0
    hyphen = 0
    comma = 0
    period = 0

    if not isNumber(text) and not type(text) == float:
        for i in range (0, len(str(text))):
            txt = text[i]
            if txt in ('!', "," ,"\'" ,";" ,"\"",":", ".", "-" ,"?"):  
                if txt == ':':
                    colon = colon + 1
                elif txt == ';':
                    semicolon = semicolon + 1
                elif txt == '-':
                    hyphen = hyphen + 1
                elif txt == ',':
                    comma = comma + 1
                elif txt == '.':
                    period = period + 1
                count = count + 1

    return [count,colon,semicolon,hyphen,comma,period]

def isCurreny(text):
    return 1 if text in curreny_List else 0

def isCountry(text):
    return 1 if text in country_List else 0

def isUOM(text):
    return 1 if text in UOM_List else 0

def isKeyword(text):
    return 1 if text in keywordlist else 0


def isAmount(s):
    try:
        ptn1 = "[0-9]{1,3}[,]{1}[0-9]{3}[,]{1}[0-9]{3}[,]{1}[0-9]{3}[.]{1}[0-9]{1,4}"
        ptn2 = "[0-9]{1,3}[,]{1}[0-9]{3}[,]{1}[0-9]{3}[.]{1}[0-9]{1,4}"
        ptn3 = "[0-9]{1,3}[,]{1}[0-9]{3}[.]{1}[0-9]{1,4}"
        ptn4 = "[0-9]{1,3}[.]{1}[0-9]{1,4}"
        ptn5 = "[0-9]{1,3}[.]{1}[0-9]{3}[.]{1}[0-9]{3}[.]{1}[0-9]{3}[,]{1}[0-9]{1,4}"
        ptn6 = "[0-9]{1,3}[.]{1}[0-9]{3}[.]{1}[0-9]{3}[,]{1}[0-9]{1,4}"
        ptn7 = "[0-9]{1,3}[.]{1}[0-9]{3}[,]{1}[0-9]{1,4}"
        ptn8 = "[0-9]{1,3}[,]{1}[0-9]{1,4}"
        ptns = [ptn1,ptn2,ptn3,ptn4,ptn5,ptn6,ptn7,ptn8]
        for ptn in ptns:
            l = re.findall(ptn,s)
            l1 = [g for g in l if len(g) > 0]
        if len(l1) == 1:
            return 1
    except:
        return 0
    return 1

def w2v(key):
    missing = [0]*30
    try:
        for i in range(len(str(key))):
            txt = str(key)[i]
            missing[i] = ord(txt)
        return missing
    except:
        return missing

def wordshape(text):
    if not(pd.isna(text)):
        t1 = re.sub('[A-Z]', 'X',text)
        t2 = re.sub('[a-z]', 'x', t1)
        return re.sub('[0-9]', 'd', t2)
    return text

for root, subfolder, files in os.walk(src):

   if len(files) > 0:
      for filename in files:
         if filename[-4:].upper() == ".CSV":
            labels = pd.read_csv(os.path.join(root,filename))
            # labels = pd.read_csv(filepath)
            for index, row in labels.iterrows():
                text = labels.loc[index,"text"]
                if pd.isna(text):
                    continue
                # labels.loc[index,"isAlphaNumeric"] = isAlphaNumeric(str(text))
                # labels.loc[index,"isAlpha"] = isAlpha(text)
                # labels.loc[index,"isNumber"] = isNumber(text)
                # labels.loc[index,"isCurreny"] = isCurreny(text)
                # labels.loc[index,"isCountry"] = isCountry(text)
                # labels.loc[index,"isUOM"] = isUOM(text)
                # labels.loc[index,"isKeyword"] = isKeyword(text)
                # labels.loc[index,"isAmount"] = isAmount(text)

                # puncs = noOfPuncs(text)
                # labels.loc[index,"noOfPuncs"] = puncs[0]
                # labels.loc[index,"countOfColon"] = puncs[1]
                # labels.loc[index,"countOfSemicolon"] = puncs[2]
                # labels.loc[index,"countOfHyphen"] = puncs[3]
                # labels.loc[index,"countOfComma"] = puncs[4]
                # labels.loc[index,"countOfPeriod"] = puncs[5]


                if row["len_digit"] > 0 and row["len_digit"] > row["len_alpha"] and len(str(text)) > 7 and row["DATE"] == 0 and row["is_email"] == 0:
                    labels.loc[index,"isID"] = 1
                else:
                    labels.loc[index,"isID"] = 0

                # try:
                #     labels.loc[index,"wordShape"] = wordshape(text)
                # except Exception as e:
                #     print("Exception ", e,"\nFilename: ",filename, "\nText: ", text)


            labels["isAlphaNumeric"] = labels['text'].apply(isAlphaNumeric)
            labels["isAlpha"] = labels['text'].apply(isAlpha)
            labels["isKeyword"] = labels['text'].apply(isKeyword)
            labels["isCurreny"] = labels['text'].apply(isCurreny)
            labels["isUOM"] = labels['text'].apply(isUOM)
            labels["isCountry"] = labels['text'].apply(isCountry)
            labels["isAmount"] = labels['text'].apply(isAmount)
            labels["wordshape"] = labels['text'].apply(wordshape)
            labels["noOfPuncs_list"] = labels['text'].apply(noOfPuncs)
            labels[noOfPuncs_list] = labels["noOfPuncs_list"].apply(foo)


            labels['vector'] = labels['text'].apply(w2v)
            labels[text_emb] = labels["vector"].apply(foo)
            labels[rev_emb] = labels["vector"].apply(oof)

            labels['vector'] = labels['wordshape'].apply(w2v)
            labels[shape_emb] = labels["vector"].apply(foo)

            del labels['vector']
            del labels['wordshape']
            del labels["noOfPuncs_list"]

            labels.to_csv(os.path.join(root,filename))

