from flask import (Flask, request, render_template,
                    make_response, after_this_request,
                    redirect, url_for)
from webbrowser import open as webopen

# Setup Flask
web = Flask(__name__)

@web.route('/')
def index():
    # If cookie exists, it gets returned
    try:
        resp = request.cookies['user']
    except KeyError:
        # Otherwise go to the login page
        resp = redirect('/login')
    resp = render_template('playlist.html')
    return resp

@web.route('/login', methods=['GET', 'POST'])
def login():
    # If we are POSTing:
    # 1. grab the username
    # 2. redirect to the index using a response
    # 3. Set the cookie
    if request.method == 'POST':
        username = request.form['user']
        resp = make_response(redirect('/'))
        resp.set_cookie('user', username)
        return resp
    else:
        # If GETing show a login form
        ret = render_template('login.html')
    return ret

if __name__ == '__main__':
    port = 5000
    webopen('localhost:'+str(port), 2)
    web.run(debug=True, host='0.0.0.0', port=port)
    
