import os
import requests

from flask import Flask, request, redirect, session, render_template, url_for
from requests_oauthlib import OAuth2Session

# Setup Flask
auth = Flask(__name__)

# Spotify details
# ~ # Jacks_Party_Jukebox client ID and secret
# ~ client_id = 'e140630233fe4f4098be987729b8693d'
# ~ client_secret = 'f261fdb4760e4134b9b5228e625ad989'
# Spotify's authentication and token exchange URLs
spotify_auth = 'https://accounts.spotify.com/authorize'
spotify_token = 'https://accounts.spotify.com/api/token'

# Struct for client
class Client(object):
    def __init__(self, client_id, client_secret):
        self.id = client_id
        self.secret = client_secret

def auth(webapp, client, scope=['user-read-private']):
    
    @webapp.route('/obtain_token')
    def stage_1():
        spot = OAuth2Session(   client.id,
                                redirect_uri='http://127.0.0.1:6500/callback',
                                scope=scope)
        authorization_url, state = spot.authorization_url(spotify_auth)

        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        return redirect(authorization_url)

    @webapp.route('/callback')
    def callback():
        print('Authenticated')
        code = request.args['code']
        print('Exchange code is:', code)
        spot = OAuth2Session(   client.id,
                                redirect_uri='http://127.0.0.1:6500/callback',
                                state=session['oauth_state'])
        print('provided URL is:', request.url)
        token = spot.fetch_token(spotify_token,
                                    client_secret=client.secret,
                                    authorization_response=request.url)
        print('Got token:', token)
        session['client_id'] = client.id
        session['oauth_token'] = token
        
        return redirect('/login/1')
        
    @webapp.route('/update_token')
    def update_token():
        extra = {'client_id' : client.id, 'client_secret' : client.secret}
        saver = lambda tok : session.update({'oauth_token' : tok})
        spot = OAuth2Session(   client.id,
                                token=session['oauth_token'],
                                auto_refresh_url=spotify_token,
                                auto_refresh_kwargs=extra,
                                token_updater=saver)
        spot.refresh_token(spotify_token)
        return redirect('/')
    
    @webapp.route('/something')
    def something():
        try:
            spot = OAuth2Session(client.id, token=session['oauth_token'])
        except KeyError:
            return redirect('/obtain_token')
        endpoint = 'https://api.spotify.com/v1/me/player/next'
        #spot.post(endpoint)
        ret = spot.get('https://api.spotify.com/v1/search', params={'q':'hello', 'type':'track'})
        import pprint
        nice = pprint.pformat(str(ret.json()))
        return ret.json()
        
    return (stage_1, callback, something)


