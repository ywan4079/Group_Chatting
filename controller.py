'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, Bottle,static_file

import model


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

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    username = request.query.get('user')
    return model.index(username)

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.login_form()

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
    username = request.forms.get('username')
    password = request.forms.get('password')
    
    # Call the appropriate method
    return model.login_check(username, password)

#-----------------------------------------------------------------------------

#Display friend list page
@get('/friends')
def show_friends():
    username = request.query.get('user')
    return model.friends(username)

#-----------------------------------------------------------------------------

#get which user is going chat with
@post("/chat")
def chat():
    username = request.forms.get('user').split(',')[0]
    recipient = request.forms.get('user').split(',')[1]
    return model.chat(username, recipient)

#-----------------------------------------------------------------------------

#get message and update chat records
@post("/send_msg")
def send_msg():
    msg = request.forms.get('msg')
    username = request.query.get('user')
    recipient = request.query.get('recipient')
    return model.send_msg(msg, username, recipient)

#-----------------------------------------------------------------------------

@get('/logout')
def logout():
    username = request.query.get('user')
    return model.logout(username)


#-----------------------------------------------------------------------------


@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    username = request.query.get('user')
    return model.about(username)
#-----------------------------------------------------------------------------

#display sign up page
@get('/sign_up')
def show_sign_up_page():
    return model.show_sign_up_page()

#-----------------------------------------------------------------------------

#attempt to sign up
@post('/sign_up')
def sign_up_check():
    username = request.forms.get('username')
    password = request.forms.get('password')
    password_2 = request.forms.get('password_2')
    return model.sign_up_check(username, password, password_2)

#-----------------------------------------------------------------------------

#display add friends page
@get('/add_friends')
def show_add_friends():
    username = request.query.get('user')
    return model.show_add_friends(username)

#-----------------------------------------------------------------------------

#attempt to add friends
@post('/add_friends')
def add_friends_check():
    username = request.query.get('user')
    recipient = request.forms.get('username')
    return model.add_friends_check(username, recipient)

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
