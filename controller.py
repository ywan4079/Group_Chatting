'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, Bottle,static_file

import model
import os
import json


#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow video loading
@route('/video/<video:path>')
def serve_pictures(video):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(video, root='static/video/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Display the login page
@get('/')
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    uid = request.query.get('uid')
    return model.login_page(uid)

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    unikey = request.forms.get('unikey')
    psw = request.forms.get('psw')
    
    # Call the appropriate method
    return model.login_check(unikey, psw) ###

@get('/register')
def register_page():
    return model.register_page()

@post('/register')
def register_check():
    username = request.forms.get('username')
    unikey = request.forms.get('unikey')
    psw = request.forms.get('psw')
    psw2 = request.forms.get('psw2')
    question = request.forms.get('questions')
    answer = request.forms.get('answer')

    return model.register_check(username, unikey, psw, psw2, question, answer)

####################################################

@get('/reset_psw')
def reset_psw():
    return model.reset_psw()

@post('/reset_psw')
def reset_psw_check():
    username = request.forms.get('username')
    unikey = request.forms.get('unikey')
    question = request.forms.get('questions')
    answer = request.forms.get('answer')
    psw = request.forms.get('npsw')
    psw2 = request.forms.get('npsw2')
    return model.reset_psw_check(username, unikey, question, answer, psw, psw2)

####################################################

@get('/default_sidebar')
def default():
    uid = request.query.get('uid')
    username = request.query.get('username')
    return model.default(uid, username)

@get('/sidebar_chat')
def chat_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    return model.chat_page(uid, username, target_id, target_name)

@post('/sidebar_chat')
def send_msg():
    msg = request.forms.get('msg')
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    return model.send_msg(msg, uid, username, target_id, target_name)



@get('/chat_setting')
def chat_setting():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    return model.chat_setting(uid, username, target_id, target_name)

@get('/chat_history_page')
def chat_history_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    return model.chat_history_page(uid, username, target_id, target_name)

@post('/chat_history')
def chat_history_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    search_word = request.forms.get('history')
    return model.chat_history(uid, username, target_id, target_name, search_word)

@get('/clear_history')
def clear_history():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    with open(f'chat_records/{uid}_{target_id}', 'wb') as f:
        f.write(b'')
    return model.chat_page(uid, username, target_id, target_name)

@post('/stick_top')
def stick_top():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    sticky = request.forms.get('sticky')  #on or None
    with open('info.json', 'r') as f:
        data = json.load(f)
        if (sticky != None):
            for i in range(len(data['user_info'])):
                if data['user_info'][i]['unikey'] == uid:
                    if (target_id.isnumeric()): #is group
                        data['user_info'][i]['top_groups'].append(str(target_id))
                    else:
                        data['user_info'][i]['top_friends'].append(target_id)
        else:
            for i in range(len(data['user_info'])):
                if data['user_info'][i]['unikey'] == uid:
                    if (target_id.isnumeric()): #is group
                        data['user_info'][i]['top_groups'].remove(str(target_id))
                    else:
                        data['user_info'][i]['top_friends'].remove(target_id)

    with open('info.json', 'w') as f:
        json.dump(data, f, indent=2)
    return model.chat_setting(uid, username, target_id, target_name) 

@get('/add_group_page')
def add_group_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    return model.add_group_page(uid, username)

@post('/add_group')
def add_group():
    uid = request.query.get('uid')
    username = request.query.get('username')
    num = request.query.get('num')
    groupname = request.forms.get('groupname')
    result = []
    for i in range(int(num)):
        r = request.forms.get(f'checkbox{i}')
        if r != None: result.append(r)
    result.append(uid)

    return model.add_group(uid, username, result, groupname)

@post('/sendimg')
def sendimg():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    img = request.files.get('sendimage')
    path = 'img/records/'
    if os.path.exists(f"static/img/records/{img.filename}"):
        i = 0
        while 1:
            if os.path.exists(f"static/img/records/{i}"):
                i+=1
                continue
            img.save(f"static/img/records/{i}")
            path += f"{i}"
            break
    else:
        img.save(f"static/img/records/"+img.filename)
        path += img.filename

    return model.sendimg(uid, username, target_id, target_name, path)

@post('/sendvideo')
def sendvideo():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    video = request.files.get('sendvideo')
    path = 'video/'
    if os.path.exists(f"static/video/{video.filename}"):
        i = 0
        while 1:
            if os.path.exists(f"static/video/{i}"):
                i+=1
                continue
            video.save(f"static/video/{i}")
            path += f"{i}"
            break
    else:
        video.save(f"static/video/"+video.filename)
        path += video.filename
    
    print(path)
    return model.sendvideo(uid, username, target_id, target_name, path)


####################################################

@get('/sidebar_contact')
def contact_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    return model.contact_page(uid, username)

@get('/add_friends_page')
def add_friends_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    return model.add_friends_page(uid, username)

@get('/add_friend')
def add_friend():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    return model.add_friend(uid, username, target_id, target_name)

@get('/unfriend')
def unfriend():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')

    return model.unfriend(uid, username, target_id, target_name)

@get('/user_detail')
def user_detail():
    uid = request.query.get('uid')
    username = request.query.get('username')
    target_id = request.query.get('target_id')
    target_name = request.query.get('target_name')
    return model.user_detail(uid, username, target_id, target_name)

####################################################

@get('/sidebar_forum')
def forum_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    return model.forum_page(uid, username)

@get('/sidebar_setting')
def setting_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    return model.setting_page(uid, username)

@get('/update_name_page')
def update_name_page():
    uid = request.query.get('uid')
    username = request.query.get('username')
    return model.update_name_page(uid, username)

@post('/update_name')
def update_name():
    uid = request.query.get('uid')
    username = request.query.get('username')
    newname = request.forms.get('newname')
    return model.update_name(uid, username, newname)

@post('/uploadimg')
def uploadimg():
    uid = request.query.get('uid')
    username = request.query.get('username')
    if os.path.exists(f"./static/img/user_icon/{uid}.png"):
        os.remove(f"./static/img/user_icon/{uid}.png")
    img = request.files.get('uploadimage')
    img.save(f"./static/img/user_icon/{uid}.png")
    return model.setting_page(uid, username)

#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
