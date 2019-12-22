from flask import Flask, request, redirect, session, render_template, url_for
from requests_oauthlib import OAuth2Session

import os
import requests

# Setup Flask
web = Flask(__name__)

# Spotify details
# Jacks_Party_Jukebox client ID and secret
client_id = 'e140630233fe4f4098be987729b8693d'
client_secret = 'f261fdb4760e4134b9b5228e625ad989'
# Spotify's authentication and token exchange URLs
spotify_auth = 'https://accounts.spotify.com/authorize'
spotify_token = 'https://accounts.spotify.com/api/token'

# Path to index page
@web.route('/obtain_token')
def index():
    scope = ['user-modify-playback-state']
    spot = OAuth2Session(   client_id,
                            redirect_uri='http://127.0.0.1:6500/callback',
                            scope=scope)
    authorization_url, state = spot.authorization_url(spotify_auth)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)

@web.route('/callback')
def callback():
    print('Authenticated')
    code = request.args['code']
    print('Exchange code is:', code)
    spot = OAuth2Session(   client_id,
                            redirect_uri='http://127.0.0.1:6500/callback',
                            state=session['oauth_state'])
    print('provided URL is:', request.url)
    token = spot.fetch_token(spotify_token,
                                client_secret=client_secret,
                                authorization_response=request.url)
    print('Got token:', token)
    session['oauth_token'] = token
    
    return redirect(url_for('.something'))
    
@web.route('/something')
def something():
    spot = OAuth2Session(client_id, token=session['oauth_token'])
    endpoint = 'https://api.spotify.com/v1/me/player/next'
    #spot.post(endpoint)
    ret = spot.get('https://api.spotify.com/v1/search', params={'q':'hello', 'type':'track'})
    return str(ret.json())

# Run when called
if __name__ == '__main__':
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    web.secret_key = os.urandom(24)
    web.run(debug=False, host='0.0.0.0', port=6500) #ssl_context='adhoc'


