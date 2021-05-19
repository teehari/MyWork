from cryptography.fernet import Fernet
import json
import ast

def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
#    print(key)
    return key

def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()

def encrypt_message(message,key):
    """
    Encrypts a message
    """
    f = Fernet(key)
    encrypted_message = f.encrypt(message)

#    print("Encripted Messages: ",message, encrypted_message)

    return encrypted_message

def decrypt_message(encripted_message,key):

    f = Fernet(key)
    decrypted_message = f.decrypt(encripted_message)
#    print("Decripted Messages: ",encripted_message, decrypted_message)
    return decrypted_message

if __name__ == "__main__":
    message = b'{"apim_key":"f761839e80d744ae95bcfa23a665690c","post_url":"https://invrecognition.cognitiveservices.azure.com/formrecognizer/v2.0-preview/Layout/analyze"}'

    key = generate_key()
    encrypted_msg = encrypt_message(message, key)
    json_str = b'{"key":"' + key + b'",' + b'"message":"' + encrypted_msg + b'"}'
#    print(json_str)
    with open("encryption_azure.json","wb") as f:
        f.write(json_str)

    with open("encryption_azure.json","rb") as f:
        txt = f.read()
        txt = txt.decode("utf-8")
    
#    print(txt)
#    text = json.dumps(txt.decode("utf-8"))
    obj = json.loads(txt)
    key = obj["key"]
    encrypted_message = obj["message"]
    decrypted_message = decrypt_message(bytes(encrypted_message,'utf-8'),key)
    decrypted_message = decrypted_message.decode('utf-8')
    decrypted_obj = ast.literal_eval(decrypted_message)
    print("Decrypted Values: ", decrypted_obj["apim_key"], decrypted_obj["post_url"])
