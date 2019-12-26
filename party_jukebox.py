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
AUTH = None
secret_user = str(sample(range(1000,10000), 1)[0])
# Setup auth
client = sa.spotify_auth.Client(CID, CSEC)
obj = sa.spotify_auth.auth(jukebox, client)

@jukebox.route('/')
def index():
    '''
    Index of jukebox, shows current playing song and queue
    '''
    if AUTH is None:
        resp = redirect('/setup')
    else:
        # If cookie exists, it gets returned
        try:
            user = request.cookies['user']
            session['user'] = user
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
    return redirect('/obtain_token')

@jukebox.route('/login', defaults={'admin' : False}, methods=['GET', 'POST'])
@jukebox.route('/login/<admin>', methods=['GET', 'POST'])
def login(admin):
    '''
    Login assigns everyone a username
    '''
    global AUTH
    if request.method == 'POST':
        username = request.form['user']
        resp = make_response(redirect('/'))
        session['user'] = username
        resp.set_cookie('user', username)
    else:
        if admin:
            AUTH = session['oauth_token']
            mesg = 'You are the session admin, use code '
            mesg += secret_user
            mesg += ' to log in to admin account'
        else:
            mesg = ''
        resp = render_template('login.html', info=mesg)
    return resp

@jukebox.route('/search', methods=['GET', 'POST'])
def search():
    '''
    Finding new songs
    '''
    global AUTH, CID
    if request.method == 'POST':
        try:
            spot = OAuth2Session(CID, token=AUTH)
        except KeyError:
            return redirect('/obtain_token')
        fform = request.form
        string = request.form['string']
        qtype = []
        for key in ['track', 'artist', 'album', 'playlist']:
            if request.form.get(key, '') == 'on':
                qtype.append(key)
        results = sa.search(spot, string, qtype)
        resp = render_template('search_results.html', user=session['user'], results=results)
    else:
        resp = render_template('search.html', user=session['user'])
    return resp

@jukebox.route('/action/<x>')
def action(x, dest='/'):
    global AUTH, CID
    try:
        spot = OAuth2Session(CID, token=AUTH)
    except KeyError:
        return redirect('/obtain_token')
    call = getattr(sa, x)
    call(spot)
    return redirect(dest)
    
@jukebox.route('/queue/<user>/<sid>')
def queue(user, sid):
    print(user, ':', sid)
    return redirect('/')

@jukebox.route('/vote/<user>/<idx>/<updown>')
def vote(user, idx, updown):
    print(user, ':', idx, ':', updown)
    return redirect('/')

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
