'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
import json
import random
import shutil
import os
from hashlib import md5
import rsa

# Initialise our views, all arguments are defaults for the template
page_view = view.View()

login_status = {}

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_page(uid):
    if uid != None:
        login_status[uid] = False
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(unikey, psw):
    login = False
    friends = []
    dict = {}
    with open('info.json', 'r') as f:
        data = json.load(f)
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == unikey: 
                pwd_hash = hash_calculator(psw, row['password'][1])[0]
                if pwd_hash == row['password'][0]: #both correct
                    login = True
                    username = row['username']
                    friends += row['top_groups']
                    friends += row['top_friends']
                    for g in row['groups']:
                        if g not in row['top_groups']: friends.append(g)
                    for f in row['friends']:
                        if f not in row['top_friends']: friends.append(f)

        for row in data['group_info']:
            dict[row['id']] = row['name']               
    
    if login:
        login_status[unikey] = True
        output = ""
        for f in friends:
            output += f"<a href='/sidebar_chat?uid={unikey}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
                
        return page_view('default_sidebar', uid=unikey, username=username, output=output)
    else:
        return page_view('login_invalid')

#-----------------------------------------------------------------------------
# Sign up
#-----------------------------------------------------------------------------

def register_page():
    return page_view("register")

def register_check(username, unikey, psw, psw2, question, answer):
    if (psw != psw2) :
        return page_view('register_invalid', error_msg = "You enter two different password")
    
    unikey_found = False
    with open('student.txt', 'r') as f:
        unikeys = f.read().split('\n')
        if unikey in unikeys:
            unikey_found = True
    if (not unikey_found):
        with open('staff.txt', 'r') as f:
            unikeys = f.read().split('\n')
            if unikey in unikeys:
                unikey_found = True

    if not unikey_found:
        return page_view('register_invalid', error_msg = "Invalid Unikey")
    
    with open('info.json', 'r') as f:
        data = json.load(f)

        for row in data['user_info']:
            if row['unikey'] == unikey:
                return page_view('register_invalid', error_msg = "Unikey already exists")
    
    salt = salt_generator()
    Password = hash_calculator(psw,salt)

    info = {"unikey": unikey, "username" : username, "password" : Password, "question":question, "answer": answer,"top_friends":[], "friends" : [], "top_groups":[], "groups" : []}
    data['user_info'].append(info) #add new user info the file

    with open('info.json', 'w') as f:
        json.dump(data, f, indent=2)

    #create random icon for user
    icon_path = f"./static/img/user_icon/icon{random.randint(1,5)}.png"
    dest_path = f"./static/img/user_icon/{unikey}.png"
    shutil.copyfile(icon_path, dest_path)

    return page_view("register_valid")

#-----------------------------------------------------------------------------
# Reset password
#-----------------------------------------------------------------------------

def reset_psw():
    return page_view("reset_psw")

def reset_psw_check(username, unikey, question, answer, psw, psw2):
    with open('info.json', 'r') as f:
        data = json.load(f)
        found = False
        i = 0
        for row in data['user_info']:
            if row['username'] == username and row['unikey'] == unikey and row['question'] == question and row['answer'] == answer:
                found = True
                if (psw != psw2):
                    return page_view('reset_psw_invalid', error_msg='You enter two different passwords')
                
                salt = salt_generator()
                Password = hash_calculator(psw,salt)  
                data['user_info'][i]['password'] = Password
                break
            i += 1

        if not found:
            return page_view('reset_psw_invalid', error_msg='Invalid user details')
        
    with open('info.json', 'w') as f:
        json.dump(data, f, indent=2)

    return page_view('reset_psw_valid')

#-----------------------------------------------------------------------------
# chat page
#-----------------------------------------------------------------------------

def default(uid, username):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)

        for row in data['group_info']:
            dict[row['id']] = row['name']

    output = ""
    for f in friends:
        output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"

    return page_view("default_sidebar", uid=uid, username=username, output=output)

def chat_page(uid, username, target_id, target_name):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)

        for row in data['group_info']:
            dict[row['id']] = row['name']
        
    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png'/><div class='name'>{dict[f]}</div></li></a>"

    public = ''
    private = ''
    with open("server_public.pem", "rb") as k:
        public = k.read()
    with open("server_private.pem", "rb") as k:
        private = k.read()
    public = rsa.PublicKey._load_pkcs1_pem(public)
    private = rsa.PrivateKey._load_pkcs1_pem(private)

    decrypt_msg = ''
    decrypt_html = ''

    with open(f"chat_records/{uid}_{target_id}", 'rb') as f:
        record = f.read()
        if (record == b''):
            decrypt_msg = []
        else:
            decrypt_msg = RSA_decryption(record, private)
            decrypt_msg = decrypt_msg.split('\n')
            for m in decrypt_msg:
                if m == '': continue
                content = ":".join(m.split(':')[1:])
                if m.split(':')[0] == uid:
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>' 
                    else:
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src ="img/user_icon/{uid}.png"></div><div class="outgoing-msg"><div class="outgoing-chats-msg"><p>{content}</p></div></div></div>'
                else:
                    t_uid = m.split(':')[0]
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div></div>'
                    else:
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><div class="received-msg"><div class="received-msg-inbox"><p>{content}</p></div></div></div>'
    
    
    return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)

def send_msg(msg, uid, username, target_id, target_name):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)

        for row in data['group_info']:
            dict[row['id']] = row['name']

    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png'/><div class='name'>{dict[f]}</div></li></a>"

    public = ''
    private = ''
    with open("server_public.pem", "rb") as k:
        public = k.read()
    with open("server_private.pem", "rb") as k:
        private = k.read()
    public = rsa.PublicKey._load_pkcs1_pem(public)
    private = rsa.PrivateKey._load_pkcs1_pem(private)

    decrypt_msg = ''
    decrypt_html = ''

    with open(f"chat_records/{uid}_{target_id}", 'rb') as f:
        record = f.read()
        if (record == b''):
            decrypt_msg = []
        else:
            decrypt_msg = RSA_decryption(record, private)
            decrypt_msg = decrypt_msg.split('\n')
            for m in decrypt_msg:
                if m == '': continue
                content = ":".join(m.split(':')[1:])
                if m.split(':')[0] == uid:
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>' 
                    else:
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src ="img/user_icon/{uid}.png"></div><div class="outgoing-msg"><div class="outgoing-chats-msg"><p>{content}</p></div></div></div>'
                else:
                    t_uid = m.split(':')[0]
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>'
                    else:
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><div class="received-msg"><div class="received-msg-inbox"><p>{content}</p></div></div></div>'
        
        if msg == None or msg == '':
            return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)
        
        decrypt_msg.append(f'{uid}:{msg}')
        decrypt_msg = '\n'.join(decrypt_msg)
        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src ="img/user_icon/{uid}.png"></div><div class="outgoing-msg"><div class="outgoing-chats-msg"><p>{msg}</p></div></div></div>'

        encrypt_msg = RSA_encryption(decrypt_msg, public)
    
    with open(f'chat_records/{uid}_{target_id}', 'wb') as f:
        f.write(encrypt_msg)

    if target_id.isnumeric():
        members = []
        for row in data['group_info']:
            if (str(row['id']) == target_id):
                members = row['members']
                break
        print(members)
        for m in members:
            if m ==uid: continue

            with open(f'chat_records/{m}_{target_id}', 'rb') as f:
                records = f.read()

                if records == b'':
                    decrypt_records = ''
                else:
                    decrypt_records = RSA_decryption(records, private)
                
                decrypt_records = decrypt_records.split('\n')
                decrypt_records.append(f'{uid}:{msg}')
                decrypt_records = '\n'.join(decrypt_records)

                encrypt_records = RSA_encryption(decrypt_records, public)
            
            with open(f'chat_records/{m}_{target_id}', 'wb') as f:
                f.write(encrypt_records)

        return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)
    
    with open(f'chat_records/{target_id}_{uid}', 'rb') as f:
        records = f.read()

        if records == b'':
            decrypt_records = ''
        else:
            decrypt_records = RSA_decryption(records, private)
        
        decrypt_records = decrypt_records.split('\n')
        decrypt_records.append(f'{uid}:{msg}')
        decrypt_records = '\n'.join(decrypt_records)

        encrypt_records = RSA_encryption(decrypt_records, public)
    
    with open(f'chat_records/{target_id}_{uid}', 'wb') as f:
        f.write(encrypt_records)

    return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)

def sendimg(uid, username, target_id, target_name, imgpath):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)
        for row in data['group_info']:
            dict[row['id']] = row['name']

    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png'/><div class='name'>{dict[f]}</div></li></a>"

    public = ''
    private = ''
    with open("server_public.pem", "rb") as k:
        public = k.read()
    with open("server_private.pem", "rb") as k:
        private = k.read()
    public = rsa.PublicKey._load_pkcs1_pem(public)
    private = rsa.PrivateKey._load_pkcs1_pem(private)

    decrypt_msg = ''
    decrypt_html = ''

    with open(f"chat_records/{uid}_{target_id}", 'rb') as f:
        record = f.read()
        if (record == b''):
            decrypt_msg = []
        else:
            decrypt_msg = RSA_decryption(record, private)
            decrypt_msg = decrypt_msg.split('\n')
            for m in decrypt_msg:
                if m == '': continue
                content = ":".join(m.split(':')[1:])
                if m.split(':')[0] == uid:
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>' 
                    else:
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src ="img/user_icon/{uid}.png"></div><div class="outgoing-msg"><div class="outgoing-chats-msg"><p>{content}</p></div></div></div>'
                else:
                    t_uid = m.split(':')[0]
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>'
                    else:
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><div class="received-msg"><div class="received-msg-inbox"><p>{content}</p></div></div></div>'

        decrypt_msg.append(f'{uid}:\\image:{imgpath}')
        decrypt_msg = '\n'.join(decrypt_msg)
        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><img src="{imgpath}"></p></div>'

        encrypt_msg = RSA_encryption(decrypt_msg, public)

    with open(f'chat_records/{uid}_{target_id}', 'wb') as f:
        f.write(encrypt_msg)

    if target_id.isnumeric():
        members = []
        for row in data['group_info']:
            if (str(row['id']) == target_id):
                members = row['members']
                break
        
        for m in members:
            if m ==uid: continue
            with open(f'chat_records/{m}_{target_id}', 'rb') as f:
                records = f.read()

                if records == b'':
                    decrypt_records = ''
                else:
                    decrypt_records = RSA_decryption(records, private)
                
                decrypt_records = decrypt_records.split('\n')
                decrypt_records.append(f'{uid}:\\image:{imgpath}')
                decrypt_records = '\n'.join(decrypt_records)

                encrypt_records = RSA_encryption(decrypt_records, public)
            
            with open(f'chat_records/{m}_{target_id}', 'wb') as f:
                f.write(encrypt_records)
        return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)

    with open(f'chat_records/{target_id}_{uid}', 'rb') as f:
        records = f.read()

        if records == b'':
            decrypt_records = ''
        else:
            decrypt_records = RSA_decryption(records, private)
        
        decrypt_records = decrypt_records.split('\n')
        decrypt_records.append(f'{uid}:\\image:{imgpath}')
        decrypt_records = '\n'.join(decrypt_records)

        encrypt_records = RSA_encryption(decrypt_records, public)
    
    with open(f'chat_records/{target_id}_{uid}', 'wb') as f:
        f.write(encrypt_records)

    return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)

def sendvideo(uid, username, target_id, target_name, videopath):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)

        for row in data['group_info']:
            dict[row['id']] = row['name']
        
    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png'/><div class='name'>{dict[f]}</div></li></a>"

    public = ''
    private = ''
    with open("server_public.pem", "rb") as k:
        public = k.read()
    with open("server_private.pem", "rb") as k:
        private = k.read()
    public = rsa.PublicKey._load_pkcs1_pem(public)
    private = rsa.PrivateKey._load_pkcs1_pem(private)

    decrypt_msg = ''
    decrypt_html = ''

    with open(f"chat_records/{uid}_{target_id}", 'rb') as f:
        record = f.read()
        if (record == b''):
            decrypt_msg = []
        else:
            decrypt_msg = RSA_decryption(record, private)
            decrypt_msg = decrypt_msg.split('\n')
            for m in decrypt_msg:
                if m == '': continue
                content = ":".join(m.split(':')[1:])
                if m.split(':')[0] == uid:
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>' 
                    else:
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src ="img/user_icon/{uid}.png"></div><div class="outgoing-msg"><div class="outgoing-chats-msg"><p>{content}</p></div></div></div>'
                else:
                    t_uid = m.split(':')[0]
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>'
                    else:
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><div class="received-msg"><div class="received-msg-inbox"><p>{content}</p></div></div></div>'

        decrypt_msg.append(f'{uid}:\\video:{videopath}')
        decrypt_msg = '\n'.join(decrypt_msg)
        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><video controls><source src="{videopath}" type="video/mp4"><source src="{".".join(videopath.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>'

        encrypt_msg = RSA_encryption(decrypt_msg, public)

    with open(f'chat_records/{uid}_{target_id}', 'wb') as f:
        f.write(encrypt_msg)

    if target_id.isnumeric():
        members = []
        for row in data['group_info']:
            if (str(row['id']) == target_id):
                members = row['members']
                break
        
        for m in members:
            if m ==uid: continue

            with open(f'chat_records/{m}_{target_id}', 'rb') as f:
                records = f.read()

                if records == b'':
                    decrypt_records = ''
                else:
                    decrypt_records = RSA_decryption(records, private)
                
                decrypt_records = decrypt_records.split('\n')
                decrypt_records.append(f'{uid}:\\video:{videopath}')
                decrypt_records = '\n'.join(decrypt_records)

                encrypt_records = RSA_encryption(decrypt_records, public)
            
            with open(f'chat_records/{m}_{target_id}', 'wb') as f:
                f.write(encrypt_records) 

        return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)
    
    with open(f'chat_records/{target_id}_{uid}', 'rb') as f:
        records = f.read()

        if records == b'':
            decrypt_records = ''
        else:
            decrypt_records = RSA_decryption(records, private)
        
        decrypt_records = decrypt_records.split('\n')
        decrypt_records.append(f'{uid}:\\video:{videopath}')
        decrypt_records = '\n'.join(decrypt_records)

        encrypt_records = RSA_encryption(decrypt_records, public)
    
    with open(f'chat_records/{target_id}_{uid}', 'wb') as f:
        f.write(encrypt_records) 

    return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html)

def chat_setting(uid, username, target_id, target_name):
    if target_id.isnumeric(): u_or_q = "Quit group"
    else: u_or_q = "Unfriend"
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        check = ''
        friends = []
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends += row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)
                if target_id.isnumeric() and target_id in row['top_groups']: check = "checked"
                elif (not target_id.isnumeric()) and target_id in row['top_friends']: check = "checked"

        for row in data['group_info']:
            dict[row['id']] = row['name']

    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png'/><div class='name'>{dict[f]}</div></li></a>"

    public = ''
    private = ''
    with open("server_public.pem", "rb") as k:
        public = k.read()
    with open("server_private.pem", "rb") as k:
        private = k.read()
    public = rsa.PublicKey._load_pkcs1_pem(public)
    private = rsa.PrivateKey._load_pkcs1_pem(private)

    decrypt_msg = ''
    decrypt_html = ''

    with open(f"chat_records/{uid}_{target_id}", 'rb') as f:
        record = f.read()
        if (record == b''):
            decrypt_msg = []
        else:
            decrypt_msg = RSA_decryption(record, private)
            decrypt_msg = decrypt_msg.split('\n')
            for m in decrypt_msg:
                if m == '': continue
                content = ":".join(m.split(':')[1:])
                if m.split(':')[0] == uid:
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src="img/user_icon/{uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>' 
                    else:
                        decrypt_html += f'<div class="outgoing-chats"><div class="outgoing-chats-img"><img src ="img/user_icon/{uid}.png"></div><div class="outgoing-msg"><div class="outgoing-chats-msg"><p>{content}</p></div></div></div>'
                else:
                    t_uid = m.split(':')[0]
                    if m.split(':')[1] == '\\image':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><img src="{path}"></p></div>'
                    elif m.split(':')[1] == '\\video':
                        path = m.split(':')[2]
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><p><video controls><source src="{path}" type="video/mp4"><source src="{".".join(path.split(".")[:-1])}.ogg" type="video/ogg"></video></p></div>'
                    else:
                        decrypt_html += f'<div class="received-chats"><div class="received-chats-img"><img src="img/user_icon/{t_uid}.png"></div><div class="received-msg"><div class="received-msg-inbox"><p>{content}</p></div></div></div>'

    return page_view("sidebar_chat_setting", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, msgs=decrypt_html, checked=check, u_or_q=u_or_q)

def add_group_page(uid, username):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['friends']

    friend_checkbox = ''
    selected_friend = ''
    i = 0
    for f in friends:
        friend_checkbox += f'<li><label class="container"><div class="font">{dict[f]}</div><img src="img/user_icon/{f}.png"/><input type="checkbox" name="checkbox{i}" value="{f}" id="myCheck{i}" onclick="checkBox()"> <span class="checkmark"></span></label></li>'
        selected_friend += f'<span id= "myCheck{i}_output" style= "display:none"><img src="img/user_icon/{f}.png"/>{dict[f]}</span>'
        i += 1

    return page_view("sidebar_add_group", uid=uid, username=username, friend_checkbox=friend_checkbox, selected_friend=selected_friend, num=i)

def add_group(uid, username, result, groupname):
    group_id = 0
    with open("group_num.txt", 'r') as f:
        group_id = int(f.read())
    with open("group_num.txt", 'w') as f:
        f.write(str(group_id+1))
    
    for u in result:
        with open(f"chat_records/{u}_{group_id}", 'w') as f:
            pass
    
    with open("info.json", 'r') as f:
        data = json.load(f)
    
    group_info = {"id":str(group_id), "name":groupname, "members":result}
    data['group_info'].append(group_info)

    for i in range(len(data['user_info'])):
        if data['user_info'][i]['unikey'] in result:
            data['user_info'][i]['groups'].append(str(group_id))

    with open("info.json", 'w') as f:
        json.dump(data, f, indent=2)

    icon_path = f"./static/img/user_icon/icon{random.randint(1,5)}.png"
    dest_path = f"./static/img/user_icon/{group_id}.png"

    shutil.copyfile(icon_path, dest_path)

    dict = {}
    friends = []
    for row in data['user_info']:
        dict[row['unikey']] = row['username']
        if row['unikey'] == uid:
            friends += row['groups']
            friends += row['friends']
    
    for row in data['group_info']:
        dict[row['id']] = row['name']
    


    output = ""
    for f in friends:
        output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"


    
    return page_view('default_sidebar', uid=uid, username=username, output=output)

def chat_history_page(uid, username, target_id, target_name):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        check = ''
        friends = []
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends += row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)
                if target_id.isnumeric() and target_id in row['top_groups']: check = "checked"
                elif (not target_id.isnumeric()) and target_id in row['top_friends']: check = "checked"

        for row in data['group_info']:
            dict[row['id']] = row['name']

    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png'/><div class='name'>{dict[f]}</div></li></a>"

    return page_view("sidebar_chat_history", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, checked=check, msgs='')

def chat_history(uid, username, target_id, target_name, search_word):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        check = ''
        friends = []
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends += row['top_groups']
                friends += row['top_friends']
                for g in row['groups']:
                    if g not in row['top_groups']: friends.append(g)
                for f in row['friends']:
                    if f not in row['top_friends']: friends.append(f)
                if target_id.isnumeric() and target_id in row['top_groups']: check = "checked"
                elif (not target_id.isnumeric()) and target_id in row['top_friends']: check = "checked"

        for row in data['group_info']:
            dict[row['id']] = row['name']

    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png'/><div class='name'>{dict[f]}</div></li></a>"

    public = ''
    private = ''
    with open("server_public.pem", "rb") as k:
        public = k.read()
    with open("server_private.pem", "rb") as k:
        private = k.read()
    public = rsa.PublicKey._load_pkcs1_pem(public)
    private = rsa.PrivateKey._load_pkcs1_pem(private)

    decrypt_msg = ''
    decrypt_html = ''

    with open(f"chat_records/{uid}_{target_id}", 'rb') as f:
        record = f.read()
        if (record == b''):
            decrypt_msg = []
        else:
            decrypt_msg = RSA_decryption(record, private)
            decrypt_msg = decrypt_msg.split('\n')
            for m in decrypt_msg:
                if m == '': continue
                if m.split(':')[1] == '\\image' or m.split(':')[1] == '\\video': continue
                id = m.split(":")[0]
                content = ":".join(m.split(':')[1:])

                if search_word in content:
                    decrypt_html += f'<div class="received-chats" style="margin-top: 20; margin-bottom: -10;"><div class="received-chats-img"><img src="img/user_icon/{id}.png"></div><div class="received-msg"><div class="received-msg-inbox"><p>{content}</p></div></div></div>'


    return page_view("sidebar_chat_history", uid=uid, username=username, target_id=target_id, target_name=target_name, output=output, checked=check, msgs=decrypt_html)

#-----------------------------------------------------------------------------
# contact page
#-----------------------------------------------------------------------------

def contact_page(uid, username):
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['friends']
    output = ""
    for f in friends:
        output += f"<li class='friend'><img src='img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li>"

    return page_view("sidebar_contact", uid=uid, username=username, output=output)

def add_friends_page(uid, username):
    with open('info.json', 'r') as f:
        data = json.load(f)
        usernames = []
        unikeys = []
        for row in data['user_info']:
            if row['unikey'] == uid:
                continue
            usernames.append(row['username'])
            unikeys.append(row['unikey'])
    users = "<ul id='friend-list'>"
    for i in range(len(unikeys)):
        users += f"<a href='/user_detail?uid={uid}&username={username}&target_id={unikeys[i]}&target_name={usernames[i]}' style=\"text-decoration: none; color: black;\"><li class='friend'><img src='img/user_icon/{unikeys[i]}.png'/><div class='name'>{usernames[i]}</div></li></a>"
    users += "</ul>"
    
    return page_view("sidebar_add_friends", uid=uid, username=username, users=users)

def add_friend(uid, username, target_id, target_name):
    with open(f'chat_records/{uid}_{target_id}', 'w') as f:
        f.write('')
    with open(f'chat_records/{target_id}_{uid}', 'w') as f:
        f.write('')
    
    with open('info.json', 'r') as f:
        data = json.load(f)
        for i in range(len(data['user_info'])):
            if data['user_info'][i]['unikey'] == uid:
                data['user_info'][i]['friends'].append(target_id)
            elif data['user_info'][i]['unikey'] == target_id:
                data['user_info'][i]['friends'].append(uid)

    
    with open('info.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    with open('info.json', 'r') as f:
        data = json.load(f)
        dict = {}
        for row in data['user_info']:
            dict[row['unikey']] = row['username']
            if row['unikey'] == uid:
                friends = row['friends']
    output = ""
    for f in friends:
        if f == target_id: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend selected'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
        else: output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"
    
    return page_view("sidebar_chat", uid=uid, username=username, target_id=target_id, target_name=target_name, msgs='', output=output)
    
def unfriend(uid, username, target_id, target_name):

    if (target_id.isnumeric()):
        os.remove(f"chat_records/{uid}_{target_id}")
        with open('info.json', 'r') as f:
            data = json.load(f)
            for i in range(len(data['user_info'])):
                if data['user_info'][i]['unikey'] == uid:
                    data['user_info'][i]['groups'].remove(target_id)
                    if target_id in data['user_info'][i]['top_groups']: data['user_info'][i]['top_groups'].remove(target_id)

            for i in range(len(data['group_info'])):
                if data['group_info'][i]['id'] == target_id:
                    data['group_info'][i]['members'].remove(uid)
                    break

        with open('info.json', 'w') as f:
            json.dump(data, f, indent=2)

        with open('info.json', 'r') as f:
            data = json.load(f)
            dict = {}
            for row in data['user_info']:
                dict[row['unikey']] = row['username']
                if row['unikey'] == uid:
                    friends = row['top_groups']
                    friends += row['top_friends']
                    for g in row['groups']:
                        if g not in row['top_groups']: friends.append(g)
                    for f in row['friends']:
                        if f not in row['top_friends']: friends.append(f)

            for row in data['group_info']:
                dict[row['id']] = row['name']

        output = ""
        for f in friends:
            output += f"<a href='/sidebar_chat?uid={uid}&username={username}&target_id={f}&target_name={dict[f]}' style='text-decoration: none; color: black;'><li class='friend'><img src='/img/user_icon/{f}.png' /><div class='name'>{dict[f]}</div></li></a>"

        return page_view("default_sidebar", uid=uid, username=username, output=output)
    
    else:
        os.remove(f"chat_records/{uid}_{target_id}")
        os.remove(f"chat_records/{target_id}_{uid}")

        with open('info.json', 'r') as f:
            data = json.load(f)
            for i in range(len(data['user_info'])):
                if data['user_info'][i]['unikey'] == uid:
                    data['user_info'][i]['friends'].remove(target_id)
                    if target_id in data['user_info'][i]['top_friends']: data['user_info'][i]['top_friends'].remove(target_id)
                elif data['user_info'][i]['unikey'] == target_id:
                    data['user_info'][i]['friends'].remove(uid)
                    if uid in data['user_info'][i]['top_friends']: data['user_info'][i]['top_friends'].remove(uid)

        with open('info.json', 'w') as f:
            json.dump(data, f, indent=2)

    with open('info.json', 'r') as f:
        data = json.load(f)
        usernames = []
        unikeys = []
        user_friends = []
        for row in data['user_info']:
            if row['unikey'] == uid:
                user_friends = row['friends']
                continue
            usernames.append(row['username'])
            unikeys.append(row['unikey'])
    
    users = ""
    for i in range(len(unikeys)):
        if unikeys[i] == target_id: users += f"<a href='/user_detail?uid={uid}&username={username}&target_id={unikeys[i]}&target_name={usernames[i]}' style=\"text-decoration: none; color: black;\"><li class='friend selected'><img src='img/user_icon/{unikeys[i]}.png'/><div class='name'>{usernames[i]}</div></li></a>"
        else: users += f"<a href='/user_detail?uid={uid}&username={username}&target_id={unikeys[i]}&target_name={usernames[i]}' style=\"text-decoration: none; color: black;\"><li class='friend'><img src='img/user_icon/{unikeys[i]}.png'/><div class='name'>{usernames[i]}</div></li></a>"

    main = f'<div class="header"><h1 style="text-align: center; margin-top: 50; margin-right: 100; font-size: 50;">{target_name}</h1><ul><img src=\'img/user_icon/{target_id}.png\' style="width:150; height: 150; float: right; margin-right: 100; margin-top: -130; object-fit:scale-down;"/></ul></div>'
    if target_id in user_friends:
        main += f'<a href="/sidebar_chat?uid={uid}&username={username}&target_id={target_id}&target_name={target_name}" style="text-decoration: none;"><button style="background-color: aqua;">Message</button></a> <a href="/unfriend?uid={uid}&username={username}&target_id={target_id}&target_name={target_name}" style="text-decoration: none;"><button style="background-color: rgb(227, 68, 68);">Unfriend</button></a>'
    else:
        main += f'<a href="/add_friend?uid={uid}&username={username}&target_id={target_id}&target_name={target_name}" style="text-decoration: none;"><button style="background-color: aqua; width: auto;">Add friend</button></a>'

    return page_view("sidebar_user_detail", uid=uid, username=username, target_id=target_id, target_name=target_name, users=users, main=main)

def user_detail(uid, username, target_id, target_name):
    with open('info.json', 'r') as f:
        data = json.load(f)
        usernames = []
        unikeys = []
        user_friends = []
        for row in data['user_info']:
            if row['unikey'] == uid:
                user_friends = row['friends']
                continue
            usernames.append(row['username'])
            unikeys.append(row['unikey'])
    
    users = ""
    for i in range(len(unikeys)):
        if unikeys[i] == target_id: users += f"<a href='/user_detail?uid={uid}&username={username}&target_id={unikeys[i]}&target_name={usernames[i]}' style=\"text-decoration: none; color: black;\"><li class='friend selected'><img src='img/user_icon/{unikeys[i]}.png'/><div class='name'>{usernames[i]}</div></li></a>"
        else: users += f"<a href='/user_detail?uid={uid}&username={username}&target_id={unikeys[i]}&target_name={usernames[i]}' style=\"text-decoration: none; color: black;\"><li class='friend'><img src='img/user_icon/{unikeys[i]}.png'/><div class='name'>{usernames[i]}</div></li></a>"

    main = f'<div class="header"><h1 style="text-align: center; margin-top: 50; margin-right: 100; font-size: 50;">{target_name}</h1><ul><img src=\'img/user_icon/{target_id}.png\' style="width:150; height: 150; float: right; margin-right: 100; margin-top: -130; object-fit:scale-down;"/></ul></div>'
    if target_id in user_friends:
        main += f'<a href="/sidebar_chat?uid={uid}&username={username}&target_id={target_id}&target_name={target_name}" style="text-decoration: none;"><button style="background-color: aqua;">Message</button></a> <a href="/unfriend?uid={uid}&username={username}&target_id={target_id}&target_name={target_name}" style="text-decoration: none;"><button style="background-color: rgb(227, 68, 68);">Unfriend</button></a>'
    else:
        main += f'<a href="/add_friend?uid={uid}&username={username}&target_id={target_id}&target_name={target_name}" style="text-decoration: none;"><button style="background-color: aqua; width: auto;">Add friend</button></a>'

    return page_view("sidebar_user_detail", uid=uid, username=username, target_id=target_id, target_name=target_name, users=users, main=main)

#-----------------------------------------------------------------------------
# forum page
#-----------------------------------------------------------------------------

def forum_page(uid, username):
    return page_view("sidebar_forum", uid=uid, username=username)

#-----------------------------------------------------------------------------
# setting page
#-----------------------------------------------------------------------------

def setting_page(uid, username):
    return page_view("sidebar_setting", uid=uid, username=username)

def update_name_page(uid, username):
    return page_view("sidebar_update_name", uid=uid, username=username)

def update_name(uid, username, newname):
    with open('info.json', 'r') as f:
        data = json.load(f)
        for i in range(len(data['user_info'])):
            if data['user_info'][i]['unikey'] == uid:
                data['user_info'][i]['username'] = newname
                break
    
    with open('info.json', 'w') as f:
        json.dump(data, f, indent=2)

    return page_view("sidebar_setting", uid=uid, username=newname)


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)



def salt_generator():
    random_str = " "
    base_str = "ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789"
    i = 0
    ls1 = []

    while i <= 49:
        ls1.append(random.choice(base_str))
        i += 1
    random_str = "".join(ls1)
    return random_str

def hash_calculator(msg,salt):
    obj = md5(salt.encode("utf-8"))
    obj.update(msg.encode("utf-8"))

    bs = obj.hexdigest()
    ls1 = [bs,salt]
    return ls1

def RSA_encryption(txt, key): #seperate plaintext into several chuncks
    result = []
    for n in range(0,len(txt),245):
        chuncks = txt[n:n+245]
        result.append(rsa.encrypt(chuncks.encode(), key))
    return b''.join(result)

def RSA_decryption(content, key):
    result = []
    for n in range(0,len(content),256):
        chuncks = content[n:n+256]
        result.append(rsa.decrypt(chuncks, key).decode())
    return ''.join(result)