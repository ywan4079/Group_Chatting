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
from hashlib import md5
import rsa

# Initialise our views, all arguments are defaults for the template
page_view = view.View()


login = False  # By default assume bad creds
login_status = {}
#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index(username):
    '''
        index
        Returns the view for the index
    '''
    global login_status
    if username == None or username not in login_status:
        return page_view("index")
    if login_status[username]:
        return page_view("index", header='header_in', user=username)
    else:
        return page_view("index")

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login", header='header_no_pic')

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    
    err_str = "Incorrect Username" #error massage by default is incorrect username
    login = False # By default assume bad creds
    with open('info.json', 'r') as f:
        data = json.load(f)

        for row in data['user_info']:
            if row['username'] == username: 
                pwd_hash = hash_calculator(password, row['password'][1])[0]
                if pwd_hash == row['password'][0]: #both correct
                    login = True
                    break

            if row['username'] == username:  #incorrect password
                err_str = "Incorrect Password"
            
    global login_status
    
    #if none of these if statements are executed, invalid username
    if login: 
        login_status[username] = True
        return page_view("valid", user=username,header='header_in_no_pic')
    else:
        return page_view("invalid", reason=err_str, header='header_no_pic')


#-----------------------------------------------------------------------------
# Friends
#-----------------------------------------------------------------------------

def friends(user):
    global login_status
    if user not in login_status or not login_status[user]:
        return page_view("login", header='header_no_pic')
    
    friends = []
    with open('info.json', 'r') as f:
        data = json.load(f)
        for row in data['user_info']:
            if row['username'] == user:
                friends = row['friends'] #get firends of current user
                break

    html_form = ''
    for f in friends:
        html_form += f'<button name="user" type="submit" value="{user},{f}">{f}</button>' #display user's friends as buttons
    return page_view("friend_list", header='header_in_no_pic', friends=html_form, user=user)


#-----------------------------------------------------------------------------
# Chat page
#-----------------------------------------------------------------------------
def chat(username, recipient):
    global login_status
    if username not in login_status or not login_status[username]:
        return page_view("login", header='header_no_pic')
    
    records = ''
    private = ''
    with open("key/{}_private.pem".format(username), 'rb') as k:
        private = k.read()
    private = rsa.PrivateKey._load_pkcs1_pem(private)

    with open(f'chat_records/{username}_{recipient}', 'rb') as f:
        encrypt_records = f.read()
        if encrypt_records == b'':
            records = ''
        else:
            records = RSA_decryption(encrypt_records, private) #display the chat records between specific users

    records = records.split('\n')
    records_html = ''
    for m in records:
        content = ":".join(m.split(':')[1:])
        if m.split(':')[0] == 'u':
            records_html += f'<div class="outgoing-chats">\n<div class="outgoing-msg">\n<div class="outgoing-chats-msg">\n<p class="received-msg">{content}</p>\n</div>\n</div>\n</div>'
        elif m.split(':')[0] == 'r':
            records_html += f'<div class="received-chats">\n<div class="received-msg">\n<div class="received-msg-inbox">\n<p class="single-msg">{content}</p>\n</div>\n</div>\n</div>'
    
    return page_view("chat", header='header_chatting', user=username, recipient=recipient, msgs=records_html)

#-----------------------------------------------------------------------------
# send message
#-----------------------------------------------------------------------------

def send_msg(msg, username, recipient):
    # global login_status
    # if username not in login_status or not login_status[username]:
    #     return page_view("login", header='header_no_pic')
    
    
    user_public = ''
    user_private = ''
    rec_public = ''
    rec_private = ''
    with open("key/{}_public.pem".format(username), "rb") as k:
        user_public = k.read()
    with open("key/{}_private.pem".format(username), "rb") as k:
        user_private = k.read()
    with open("key/{}_public.pem".format(recipient), "rb") as k:
        rec_public = k.read()
    with open("key/{}_private.pem".format(recipient), "rb") as k:
        rec_private = k.read()
    user_public = rsa.PublicKey._load_pkcs1_pem(user_public)
    user_private = rsa.PrivateKey._load_pkcs1_pem(user_private)
    rec_public = rsa.PublicKey._load_pkcs1_pem(rec_public)
    rec_private = rsa.PrivateKey._load_pkcs1_pem(rec_private)

    decrypt_records = ''
    decrypt_html = ''
    ###user to recipient side
    with open(f'chat_records/{username}_{recipient}', 'rb') as f:
        records = f.read()

        if records == b'':
            decrypt_records = []
        else:
            decrypt_records = RSA_decryption(records, user_private)

            decrypt_records = decrypt_records.split('\n')
            for m in decrypt_records:
                content = ":".join(m.split(':')[1:])
                if m.split(':')[0] == 'u':
                    decrypt_html += f'<div class="outgoing-chats">\n<div class="outgoing-msg">\n<div class="outgoing-chats-msg">\n<p class="received-msg">{content}</p>\n</div>\n</div>\n</div>'
                elif m.split(':')[0] == 'r':
                    decrypt_html += f'<div class="received-chats">\n<div class="received-msg">\n<div class="received-msg-inbox">\n<p class="single-msg">{content}</p>\n</div>\n</div>\n</div>'
        
        if msg == None or msg == '': #if msg is null, display the same page
            return page_view('chat', header='header_chatting', user=username, recipient=recipient, msgs=decrypt_html)

        decrypt_records.append(f'u:{msg}')
        decrypt_records = '\n'.join(decrypt_records)
        decrypt_html += f'<div class="outgoing-chats">\n<div class="outgoing-msg">\n<div class="outgoing-chats-msg">\n<p class="received-msg">{msg}</p>\n</div>\n</div>\n</div>'
                
        encrypt_records = RSA_encryption(decrypt_records, user_public)

    with open(f'chat_records/{username}_{recipient}', 'wb') as f:
        f.write(encrypt_records)

    ###recipient to user side
    with open(f'chat_records/{recipient}_{username}', 'rb') as f:
        records = f.read()

        if records == b'':
            decrypt_records = ''
        else:
            decrypt_records = RSA_decryption(records, rec_private)

        decrypt_records = decrypt_records.split('\n')
        decrypt_records.append(f'r:{msg}')
        decrypt_records = '\n'.join(decrypt_records)
                
        encrypt_records = RSA_encryption(decrypt_records, rec_public)

    with open(f'chat_records/{recipient}_{username}', 'wb') as f:
        f.write(encrypt_records)
    
    return page_view('chat', header='header_chatting', user=username, recipient=recipient, msgs=decrypt_html)


#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about(username):
    '''
        about
        Returns the view for the about page
    '''
    global login_status
    if username == None or username not in login_status:
        return page_view("index")
    if login_status[username]:
        return page_view("about", garble=about_garble(), header='header_in', user=username)
    else:
        return page_view("about", garble=about_garble())

#-----------------------------------------------------------------------------
# Sign up
#-----------------------------------------------------------------------------

def show_sign_up_page():
    return page_view("sign_up", header='header_no_pic')

#-----------------------------------------------------------------------------
# Sign up check
#-----------------------------------------------------------------------------

def sign_up_check(username, password, password_2):
    if password != password_2:
        return page_view("invalid", reason="Two passwords are different", header='header_no_pic')
    
    data = None
    with open('info.json', 'r') as f:
        data = json.load(f)

        for row in data['user_info']:
            if row['username'] == username:
                return page_view("invalid", reason="Username already exists", header='header_no_pic')
            
        salt = salt_generator()
        Password = hash_calculator(password,salt) ###
        get_key(username)
        info = {"username" : username, "password" : Password, "friends" : []}
        data['user_info'].append(info) #add new user info the file

    with open('info.json', 'w') as f:
        json.dump(data, f, indent=2)

    return page_view("sign_up_valid", header='header_no_pic')

#-----------------------------------------------------------------------------
# logout
#-----------------------------------------------------------------------------

def logout(username):
    
    global login_status
    login_status[username] = False
    return page_view("index")

#-----------------------------------------------------------------------------
# Show add friends page
#-----------------------------------------------------------------------------

def show_add_friends(username):
    global login_status
    if username not in login_status or not login_status[username]:
        return page_view("login", header='header_no_pic')
    
    return page_view('add_friends', header='header_in_no_pic', user=username)

def add_friends_check(username, recipient):
    data = None
    friend_exist = False #by default user do not exist
    if username == recipient:
        return page_view('invalid', header='header_in_no_pic', user=username, reason='It is user yourself!')

    with open('info.json', 'r') as f:
        data = json.load(f)

        for row in data['user_info']:
            if row['username'] == recipient: 
                friend_exist = True
                break
            if row['username'] == username:
                if recipient in row['friends']: #if the recipient is already user's friend
                    return page_view('invalid', header='header_in_no_pic', user=username, reason='Username is your friend')

        if not friend_exist: #if the recipient do not exist
            return page_view('invalid', header='header_in_no_pic', user=username, reason='Username do not exist')

        for i in range(len(data['user_info'])): #no error
            if data['user_info'][i]['username'] == username:
                data['user_info'][i]['friends'].append(recipient)

            if data['user_info'][i]['username'] == recipient:
                data['user_info'][i]['friends'].append(username)

    with open('info.json', 'w') as f:
        json.dump(data, f, indent=2)

    with open(f'chat_records/{username}_{recipient}', 'wb') as f:
        f.write(b'')
    with open(f'chat_records/{recipient}_{username}', 'wb') as f:
        f.write(b'')

    
    return page_view('add_valid', header='header_in_no_pic', user=username)

# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


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

def get_key(username):
    key_name = username
    (public, private) = rsa.newkeys(2048)
    with open("key/{}_public.pem".format(key_name), "wb") as f:
        f.write(public._save_pkcs1_pem())

    with open("key/{}_private.pem".format(key_name), "wb") as f:
        f.write(private._save_pkcs1_pem())

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