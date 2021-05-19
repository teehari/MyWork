# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 19:13:18 2020

@author: Hari
"""

import numpy as np
import os
import pandas as pd

inp = r"D:\Invoice Data Extraction\TAPP 3.0\lstm_24Apr2020"

tagvals = {'-pad-': 2,
 'billingaddress': 9,
 'currency': 43,
 'discountamount': 41,
 'duedate': 21,
 'entitygstin': 38,
 'freightamount': 42,
 'invoicedate': 19,
 'invoicenumber': 14,
 'itemdescription': 4,
 'itemquantity': 36,
 'itemvalue': 5,
 'lblbillingaddress': 39,
 'lblcurrency': 44,
 'lbldiscountamount': 40,
 'lblduedate': 20,
 'lblentitygstin': 12,
 'lblinvoicedate': 18,
 'lblinvoicenumber': 13,
 'lblpaymentterms': 22,
 'lblponumber': 32,
 'lblshippingaddress': 34,
 'lblsubtotal': 25,
 'lbltotalamount': 30,
 'lblvattotal': 28,
 'lblvendoremail': 15,
 'lblvendorgstin': 16,
 'paymentterms': 23,
 'ponumber': 33,
 'serviceenddate': 6,
 'servicestartdate': 3,
 'shippingaddress': 35,
 'subtotal': 26,
 'taxamount': 37,
 'taxrate': 24,
 'totalamount': 31,
 'unitprice': 7,
 'unknown': 1,
 'vatrate': 27,
 'vattotal': 29,
 'vendoraddress': 11,
 'vendoremail': 8,
 'vendorgstin': 17,
 'vendorname': 10}

vs = tagvals.values()
tagnames = {}
for v in vs:
    for tagval in tagvals:
        if tagvals[tagval] == v:
            tagnames[v] = tagval

arr = np.load(os.path.join(inp,"results_24Apr2020.npy"))

l = list(arr)

for filindx, fil in enumerate(l):
    tags = []
    tagnms = []
    tokens = list(fil)
    for token in tokens:
        val = np.argmax(token) + 1
#        tagnm = tagnames[val]
        tags.append(val)
#        tagnms.append(tagnm)
#    df = pd.DataFrame({"Tagname":tagnms,"Tagindex":tags})
    df = pd.DataFrame({"Tagindex":tags})
    df.to_excel(os.path.join(inp,"file_"+str(filindx)+".xlsx"),
                index = False)
    df = None



