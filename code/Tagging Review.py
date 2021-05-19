#!/usr/bin/env python
# coding: utf-8

# In[253]:


import pandas as pd
from datetime import datetime, timedelta


# In[254]:


date = str(datetime.now().date())

date_for_which_to_verify = str(datetime.now().date() - timedelta(days=1))

file_name = "../TAPP_DATA/Tagging_Status_" + str(date) + ".csv"
DF = pd.read_csv(file_name, index_col=0)

DF[['Client', 'Format', 'Page Name']] = DF['File Name'].str.split('-', expand=True)
DF[['a', 'b', 'c']] = DF['Page Name'].str.split('_', expand=True)
DF[['Page Num', 'Extension']] = DF['c'].str.split('.', expand=True)
DF['OriginalFile'] = DF['a'] + '_' + DF['b'] + '.' + DF['Extension']

DF.drop(['a', 'b', 'c', 'Extension'], axis=1, inplace=True)


# In[255]:


critical_fileds = [ 'lblInvoiceNumber',
 'invoiceNumber',
 'lblInvoicedate',
 'invoiceDate',
 'lblPoNumber',
 'poNumber',
 'lblDueDate',
 'dueDate',
 'lblSubTotal',
 'subTotal',
 'lblTotalAmount',
 'totalAmount',
 'lblPaymentTerms',
 'paymentTerms',
 'lblVendorGSTIN',
 'vendorGSTIN',
 'lblEntityGSTIN',
 'entityGSTIN'
 ]

line_item_fileds = ['hdr_itemCode',            
 'hdr_itemDescription',
 'hdr_itemQuantity',
 'hdr_unitPrice',
 'hdr_itemValue',
 'LI_itemCode',
 'LI_itemDescription',
 'LI_itemQuantity',
 'LI_unitPrice',
 'LI_itemValue']

address_fileds = ['vendorName',
 'vendorAddress',
 'vendorEmail',
 'shippingAddress',
 'billingAddress',           
 'customerAddress']

metadata_columns = ['Tagger Name', 'Last Modified', 'Client',
                    'Format', 'OriginalFile', 'Page Num', 'File Name']

columns = metadata_columns + critical_fileds + line_item_fileds + address_fileds


# In[256]:


WORKING_DF = DF[columns].sort_values(['Client', 'Format', 'OriginalFile', 'Tagger Name'])
WORKING_DF.to_csv("../TAPP_DATA/XXXXXX.csv")


# # Individual Code for Individual Clients:

# ### Flag Pages which seem to be erroneous (Non-Invoice Pages):

# In[257]:


from difflib import SequenceMatcher

client = "DIAGIO"

WORKING_DF_CLIENT = WORKING_DF.loc[WORKING_DF['Client'] == client]

formats = list(WORKING_DF_CLIENT['Format'].unique())

def similar(list_a, list_b):
    assert len(list_a) == len(list_b)
    
    average_match_score = 0.0
    for idx, val in enumerate(list_a):
        a = list_a[idx]
        b = list_b[idx]
        if not((a.upper() == "NAN") or (b.upper == "NAN")):
            average_match_score += SequenceMatcher(None, a, b).ratio()
    
    return (average_match_score/len(list_a))

WORKING_DF_CLIENT['Check Tagging of Entire Page'] = 0
WORKING_DF_CLIENT['Comment - Check Tagging of Entire Page'] = ""

for f in formats:
    print("Processing Format:", f)
    temp_format = WORKING_DF_CLIENT.loc[WORKING_DF_CLIENT['Format'] == f]
    a = temp_format.groupby(['Page Num'])[['OriginalFile']].count().reset_index()
    if a.shape[0] > 1:
        # Invoices with multiple pages tagged found
        # It is probabile that a Non-Invoice Page is tagged as Invoice Page
        # Iterate over each invoice and find Non-Invoice Pages
        # Assume that Page Num 0 is Invoice Page and is tagged in each Invoice
        print(a)
        temp_probabble_non_invoice_pages = temp_format.loc[temp_format['Page Num'] != '0']
        for index, row in temp_probabble_non_invoice_pages.iterrows():
            original_file = row['OriginalFile']
            page_num = row['Page Num']
            print("Origianl File: ", original_file)
            row_page_0 = temp_format.loc[(temp_format['OriginalFile'] == original_file) & 
                                        (temp_format['Page Num'] == '0')]
            if (row_page_0.shape[0] == 0):
                print("First page not yet tagged!!!!")
                continue
            list_critical_fields_0 = list(row_page_0.iloc[0][critical_fileds])
            list_critical_fields_page = list(row[critical_fileds])
            
            list_critical_fields_0 = [str(i) for i in list_critical_fields_0]
            list_critical_fields_page = [str(i) for i in list_critical_fields_page]
            
            
            critical_field_similarity = similar(list_critical_fields_0, list_critical_fields_page)
            print("Similarity in Tagged Header Fields between First Page and Page Number", page_num, ":", 
                  critical_field_similarity)
            print(0, list_critical_fields_0)
            print(page_num, list_critical_fields_page)
            if(critical_field_similarity < 0.4):
                # Flag the page and ask to check for Non Invoice Page or Tagging of Critical Fields
                print("Erroneous Page Found:", critical_field_similarity)
                WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Check Tagging of Entire Page"] = 1
                WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Comment - Check Tagging of Entire Page"] = "The page \
                                      seems to be a non-invoice page."


# ### Flag erroneous tagged label (Critical Fields and their Labels) across Formats:

# In[258]:


from collections import defaultdict
from math import isnan
from collections import Counter

def find_similarity_words(a, b):
    return SequenceMatcher(None, str(a), str(b)).ratio()

def find_similarity_from_list(a, list_b):
    match_score = 0.0
    for idx, val in enumerate(list_b):
        b = list_b[idx]
        if not((a.upper() == "NAN") or (b.upper == "NAN")):
            match_score += SequenceMatcher(None, a, b).ratio()
    
    return (match_score/len(list_b))

WORKING_DF_CLIENT['Check Tagging of Critical Fields'] = 0
WORKING_DF_CLIENT['Comment - Check Tagging of Critical Fields'] = ""

for f in formats:
#     if f != 'Format_1084':
#         continue
    print("Processing Format:", f)
    temp_format = WORKING_DF_CLIENT.loc[(WORKING_DF_CLIENT['Check Tagging of Entire Page'] == 0) 
                                        & (WORKING_DF_CLIENT['Format'] == f)]
    list_files = (list(temp_format["OriginalFile"]))
    list_page_nums = (list(temp_format["Page Num"]))
    print(list_files)
    print(list_page_nums)
    for c in critical_fileds:
        if "lbl" in c:
            # Check for similarity of labels: As label for critical field should be same across formats
            list_labels = list(temp_format[c])
            frequecny_lbls = defaultdict(int)
            for w in list_labels:
                if not str(w).upper() == "NAN":
                    frequecny_lbls[w] += 1
                   
            if len(frequecny_lbls) <= 1:
                # All invoices has same labels
                continue
                    
            if len(frequecny_lbls) > 1:
                # print(c)
                # print(frequecny_lbls)
                
                max_occurence = max(frequecny_lbls, key=frequecny_lbls.get)
                # print("Max Occurence: ", max_occurence)
                del frequecny_lbls[max_occurence]
                for key, value in frequecny_lbls.items():
                    simialrity_score = find_similarity_words(max_occurence, key)
                    # print("Simialrity between", max_occurence, "and", key, "is:", simialrity_score)
                    if simialrity_score < 0.5:
                        WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT[c] == key)), "Check Tagging of Critical Fields"] = 1
                        WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT[c] == key)), 
                                              "Comment - Check Tagging of Critical Fields"] += str(" " + c)
        elif "TOTAL" in c.upper():
            list_total_fields = list(temp_format[c])
            list_total_fields = [str(i) for i in list_total_fields]
            #print(c, list_total_fields)
            
            Counter(list_total_fields)
            count_nan = list_total_fields.count('nan')
            #print(count_nan)
            for index, val in enumerate(list_total_fields):
                original_file = list_files[index]
                page_num = list_page_nums[index] 
                #print(original_file, page_num, val)
                count_digits = sum(c.isdigit() for c in val)
                count_letters = sum(c.isalpha() for c in val)
                if (count_nan < len(list_total_fields)/2) & (count_letters > count_digits):
                    #print("Probable Non-Amount field")
                    WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Check Tagging of Critical Fields"] = 1
                    WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Comment - Check Tagging of Critical Fields"] += str(" " + c)
        else:
            list_fields = list(temp_format[c])
            list_fields = [str(i) for i in list_fields]
            print(c, list_fields)
            Counter(list_fields)
            count_nan = list_fields.count('nan')
            if count_nan == len(list_fields):
                continue
            if count_nan <= len(list_fields)/2:
                # Mark all missing fields as to be checked
                for index, val in enumerate(list_fields):
                    if val == 'nan':
                        original_file = list_files[index]
                        page_num = list_page_nums[index] 
                        WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Check Tagging of Critical Fields"] = 1
                        WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Comment - Check Tagging of Critical Fields"] += str(" " + c)
            list_fields_non_NAN = [n for n in list_fields if n != 'nan']
            for index, val in enumerate(list_fields):
                if val == 'nan':
                    continue
                score = find_similarity_from_list(val, list_fields_non_NAN)
                if score < 0.40:
                    print(val, score)
                    original_file = list_files[index]
                    page_num = list_page_nums[index] 
                    WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Check Tagging of Critical Fields"] = 1
                    WORKING_DF_CLIENT.loc[((WORKING_DF_CLIENT['Format'] == f) & 
                                       (WORKING_DF_CLIENT['OriginalFile'] == original_file) &
                                      (WORKING_DF_CLIENT['Page Num'] == page_num)),
                                      "Comment - Check Tagging of Critical Fields"] += str(" " + c)


# In[266]:


WORKING_DF_CLIENT.to_excel("../TAPP_DATA/TAGGING_VALIDATION.xlsx", engine='openpyxl')


# In[ ]:





# In[269]:


WORKING_DF_CLIENT.loc[WORKING_DF_CLIENT['Check Tagging of Critical Fields'] == 1].groupby(['Tagger Name'])[['OriginalFile']].count()


# In[130]:


WORKING_DF_CLIENT.loc[WORKING_DF_CLIENT['Check Tagging'] == 1]


# In[ ]:




