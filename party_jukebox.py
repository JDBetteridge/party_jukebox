import os

import spotify_api as sa

from flask import (Flask, request, render_template,
                    make_response,
                    redirect, url_for, session)
from requests_oauthlib import OAuth2Session
from random import sample

# Setup Flask
jukebox = Flask(__name__)

# Spotify details
# Jacks_Party_Jukebox client ID and secret
CID = 'e140630233fe4f4098be987729b8693d'
CSEC = 'f261fdb4760e4134b9b5228e625ad989'
authenticated = False
secret_user = str(sample(range(1000,10000), 1)[0])
# Setup auth
client = sa.spotify_auth.Client(CID, CSEC)
obj = sa.spotify_auth.auth(jukebox, client)

@jukebox.route('/')
def index():
    '''
    Index of jukebox, shows current playing song and queue
    '''
    global authenitcated
    if not authenticated:
        resp = redirect('/setup')
    else:
        # If cookie exists, it gets returned
        try:
            user = request.cookies['user']
            resp = render_template('playlist.html', user=user)
        except KeyError:
            # Otherwise go to the login page
            resp = redirect('/login')
    
    return resp

@jukebox.route('/setup')
def setup():
    '''
    Setup logs "admin" into their spotify account
    '''
    global authenticated
    
    authenticated=True
    return redirect(url_for('stage_1'))

@jukebox.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Login assigns everyone a username
    '''
    if request.method == 'POST':
        username = request.form['user']
        resp = make_response(redirect('/'))
        session['user'] = username
        resp.set_cookie('user', username)
    else:
        resp = render_template('login.html')
    return resp

@jukebox.route('/search', methods=['GET', 'POST'])
def search():
    '''
    Finding new songs
    '''
    if request.method == 'POST':
        # TODO:
        resp = render_template('search.html')
    else:
        resp = render_template('search.html', user=session['user'])
    return resp

@jukebox.route('/action/<x>')
def action(x, dest='/'):
    try:
        spot = OAuth2Session(session['client_id'], token=session['oauth_token'])
    except KeyError:
        return redirect('/obtain_token')
    call = getattr(sa, x)
    call(spot)
    return redirect(dest)
    

# Run party jukebox
if __name__ == '__main__':
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    
    # Sepcify port
    port = 6500
    
    # Open webpage
    #webopen('localhost:'+str(port), 2)
    
    # Secret key (shhh!)
    jukebox.secret_key = os.urandom(24)
    
    # Runs web application
    # add threaded=True
    jukebox.run(debug=True, host='0.0.0.0', port=port) #ssl_context='adhoc'
