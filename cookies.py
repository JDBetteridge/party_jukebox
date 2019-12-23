from flask import (Flask, request, render_template,
                    make_response, after_this_request,
                    redirect, url_for)

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
        ret = '''
        <form method="post">
            <p><input type=text name=user>
            <p><input type=submit value=Enter>
        </form>
        '''
    return ret

if __name__ == '__main__':
    web.run(debug=False, host='0.0.0.0', port=5000)
