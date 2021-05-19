# -*- coding: utf-8 -*-
"""
Created on Fri May 15 15:23:12 2020

@author: Hari
"""

import pandas as pd
import datetime
import seaborn as sns
date = str(datetime.datetime.now().date())
total_page_count = 9875
threshold_pages = 50
taggers = ["Suma",
"Nowfal",
"Aniket",
"Krishna",
"Suraj",
"Srikanth",
"Karri",
"Pratheeksha",
"Dulasinarkani",
"Vikas",
"Manjunath",
"Pavani",
"Moulika",
"Sriram",
"Leanda2"]
file_name = "../TAPP_DATA/Tagging_Status_" + str(datetime.datetime.now().date()) + ".csv"
DF = pd.read_csv(file_name, index_col=0)
files_tagged_overall = DF.groupby(["Tagger Name"]).agg(Total_Pages_Tagged = ('File Name', 'count')).reset_index()
files_tagged_today = DF.loc[DF['Last Modified'] == date].groupby(["Tagger Name"]).agg(
    Pages_Tagged_Today = ('File Name', 'count')).reset_index()
res = files_tagged_overall.merge(files_tagged_today, on='Tagger Name', how='left')
label_cols = [
    'vendorName', 'vendorAddress', 'lblVendorEmail', 'vendorEmail',
       'billingAddress', 'lblVendorGSTIN', 'vendorGSTIN', 'lblEntityGSTIN',
       'entityGSTIN', 'lblInvoicedate', 'invoiceDate', 'lblInvoiceNumber',
       'invoiceNumber', 'hdr_itemQuantity', 'hdr_unitPrice', 'hdr_itemValue',
       'lblPoNumber', 'poNumber', 'lblVATRate', 'lblVATTotal', 'VATRate',
       'VATTotal', 'lblDueDate', 'lblSubTotal', 'subTotal', 'lblTotalAmount',
       'totalAmount', 'hdr_itemDescription', 'lblBillingAddress', 'dueDate',
       'currency', 'lblTaxAmount', 'taxAmount', 'lblCustomerName',
       'customerName', 'hdr_itemCode', 'lblVendorAddress', 'lblCurrency',
       'lblShippingAddress', 'shippingAddress', 'lblPaymentTerms',
       'paymentTerms', 'customerAddress', 'lblVendorName',
       'LI_itemDescription', 'LI_itemValue', 'lblCustomerAddress',
       'LI_itemQuantity', 'hdr_UOM', 'hdr_serviceStartDate',
       'hdr_serviceEndDate', 'hdr_taxRate', 'lblCustomerId', 'customerId',
       'hdr_taxAmount', 'hdr_ISGTRate', 'lblIGSTAmount', 'IGSTAmount',
       'lblIGSTRate', 'IGSTRate', 'LI_unitPrice', 'lblAmountPaid',
       'amountPaid', 'LI_taxRate', 'LI_taxAmount', 'LI_itemCode',
       'lblFreightAmount', 'freightAmount', 'LI_serviceStartDate',
       'LI_serviceEndDate', 'LI_UOM']
labels_tagged_overall = pd.DataFrame(DF.loc[DF['Last Modified']
                             == date].groupby(["Tagger Name"])[label_cols].count().sum(axis=1),
                                   columns=['Labels_Tagged_Overall']).reset_index()
labels_tagged_today = pd.DataFrame(DF.loc[DF['Last Modified']
                             == date].groupby(["Tagger Name"])[label_cols].count().sum(axis=1),
                                   columns=['Labels_Tagged_Today']).reset_index()
res = res.merge(labels_tagged_overall, on='Tagger Name', how='left')
res = res.merge(labels_tagged_today, on='Tagger Name', how='left')
res.fillna(0, inplace=True)
res = res.astype(int, errors="ignore")
list_taggers_present = list(res['Tagger Name'])
list_no_files_tagged = list(set(taggers) - set(list_taggers_present))
for l in list_no_files_tagged:
    res = res.append(pd.Series([l, 0, 0, 0, 0], index=res.columns), ignore_index=True)
res = res.append(pd.Series(["Total Pages Tagged", res['Total_Pages_Tagged'].sum(), res['Pages_Tagged_Today'].sum(),
                            '', ''], index=res.columns), ignore_index=True)
res = res.append(pd.Series(["Pages Left", total_page_count -
                            res.loc[res['Tagger Name'] == 'Total Pages Tagged']['Total_Pages_Tagged'].iloc[0],
                            0, '', ''], index=res.columns), ignore_index=True)
styles_font = []
def custom_styles_font(val):
    # price column styles
    if val.name == 'Tagger Name':
        # red prices with 0
        for i in val:
            #styles.append('color: %s' % ('red' if i == 'Green' else 'black'))
            styles_font.append('font-size: %s' % ('15pt' if (i == 'Total Pages Tagged'
                                                             or i == 'Pages Left') else '10pt'))
        return styles_font
    if val.name == 'Total_Pages_Tagged':
        return styles_font
    # other columns will be yellow
    return ['background-color: '] * len(val)
styles_color = []
def custom_styles_color(val):
    # price column styles
    if val.name == 'Tagger Name':
        # red prices with 0
        for i in val:
            #styles_color.append('color: %s' % ('red' if i == 'Green' else 'black'))
            styles_color.append('background-color: %s' % ('#EBDEF0' if (i == 'Total Pages Tagged'
                                                                        or i == 'Pages Left')
                                                          else ''))
        return styles_color
    if val.name == 'Total_Pages_Tagged':
        return styles_color
    # other columns will be yellow
    return ['background-color: '] * len(val)
res.style.background_gradient(cmap=sns.diverging_palette(10, 120, s=99, l=70,as_cmap=True),
                              subset=pd.IndexSlice[0:len(taggers)-1,
                                                   ['Pages_Tagged_Today']]).apply(
    custom_styles_font).apply(custom_styles_color)