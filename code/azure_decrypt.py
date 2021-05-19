# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 11:35:29 2021

@author: Hari
"""

from cryptography.fernet import Fernet
import json
import ast


def decrypt_message(encripted_message,key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encripted_message)
    return decrypted_message

def decrypt_azure ():

    with open("encryption_azure.json","rb") as f:
        txt = f.read()
        txt = txt.decode("utf-8")

    obj = json.loads(txt)
    key = obj["key"]
    encrypted_message = obj["message"]
    decrypted_message = decrypt_message(bytes(encrypted_message,'utf-8'),key)
    decrypted_message = decrypted_message.decode('utf-8')
    decrypted_obj = ast.literal_eval(decrypted_message)
    apim_key = decrypted_obj["apim_key"]
    post_url = decrypted_obj["post_url"]
    return apim_key, post_url
