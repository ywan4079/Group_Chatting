
import model
import rsa
import os

public = ''
private = ''

def get_key(username):
    key_name = username
    (public, private) = rsa.newkeys(2048)
    with open("key/{}_public.pem".format(key_name), "wb") as f:
        f.write(public._save_pkcs1_pem())

    with open("key/{}_private.pem".format(key_name), "wb") as f:
        f.write(private._save_pkcs1_pem())

def get_key(username):
    key_name = username
    (public, private) = rsa.newkeys(2048)
    with open("key/{}_public.pem".format(key_name), "wb") as f:
        f.write(public._save_pkcs1_pem())

    with open("key/{}_private.pem".format(key_name), "wb") as f:
        f.write(private._save_pkcs1_pem())

files = os.listdir('chat_records')
for f in files[1:]:
    with open(f'chat_records/{f}', 'wb')as f:
        f.write(b'')