import json
import os
import requests

import spotify_auth

# Search
def search(spot, string, qtype=['track'], market='from_token', limit=20, offset=0):
    endpoint = 'https://api.spotify.com/v1/search'
    query = {}
    query['q'] = string
    query['type'] = ','.join(qtype)
    query['market'] = market
    query['limit'] = str(limit)
    query['offset'] = str(offset)
    
    print(query)
    ret = spot.get(endpoint, params=query)
    
    # ~ with open('json.txt', 'w') as fh:
        # ~ from pprint import pformat
        # ~ pretty = pformat(ret.json())
        # ~ fh.write(pretty)
    
    return ret.json()

# Album
def get_album_tracks(spot, aid=None, href=None, limit=50, offset=0):
    if href is None:
        endpoint = 'https://api.spotify.com/v1/albums/'
        endpoint += aid + '/tracks'
        options = {'limit' : limit, 'offset' : offset}
    else:
        endpoint = href
        options = {}
    ret = spot.get(endpoint, params=options)
    return ret.json()

# Artist
def get_artist_top_tracks(spot, aid=None, market='from_token'):
    endpoint = 'https://api.spotify.com/v1/artists/'
    endpoint += aid + '/top-tracks'
    options = {'market' : market}
    ret = spot.get(endpoint, params=options)
    return ret.json()

# Playlist
def get_users_playlists(spot, user=None):
    if user is None:
        user = get_current_profile(spot)
        username = user['id']
    endpoint = 'https://api.spotify.com/v1/users/'
    endpoint += username + '/playlists'
    options = {'limit' : 30}
    ret = spot.get(endpoint, params=options)
    return ret.json()

def create_playlist(spot, name='auto_playlist'):
    if name.strip() == '':
        raise ValueError
    user = get_current_profile(spot)
    username = user['id']
    endpoint = 'https://api.spotify.com/v1/users/'
    endpoint += username + '/playlists'
    options = {'name' : name}
    ret = spot.post(endpoint, data=json.dumps(options))
    print(ret)

def get_playlist_tracks(spot, pid=None, href=None, limit=100, offset=0):
    if href is None:
        endpoint = 'https://api.spotify.com/v1/playlists/'
        endpoint += pid + '/tracks'
        options = {'limit' : limit, 'offset' : offset}
    else:
        endpoint = href
        options = {}
    ret = spot.get(endpoint, params=options)
    return ret.json()

def add_playlist_tracks(spot, pid=None, href=None, uris=[]):
    if href is None:
        endpoint = 'https://api.spotify.com/v1/playlists/'
        endpoint += pid + '/tracks'
        options = {'limit' : limit, 'offset' : offset}
    else:
        endpoint = href
        options = {'uris' : uris}
    spot.post(endpoint, data=json.dumps(options))

# Track
def get_track(spot, sid):
    endpoint = 'https://api.spotify.com/v1/tracks/'
    ret = spot.get(endpoint+sid)
    return ret.json()

# Player
def play(spot, context_uri=None, uris=[]):
    endpoint = 'https://api.spotify.com/v1/me/player/play'
    if (context_uri is None) and (len(uris) == 0):
        spot.put(endpoint)
    elif len(uris) > 0:
        options = {'uris' : uris}
        spot.put(endpoint, data=json.dumps(options))
    elif context_uri is not None:
        options = {'context_uri' : context_uri}
        spot.put(endpoint, data=json.dumps(options))
    
def pause(spot):
    endpoint = 'https://api.spotify.com/v1/me/player/pause'
    spot.put(endpoint)
    
def skip(spot):
    endpoint = 'https://api.spotify.com/v1/me/player/next'
    spot.post(endpoint)

def previous(spot):
    endpoint = 'https://api.spotify.com/v1/me/player/previous'
    spot.post(endpoint)

def get_current(spot, market='from_token'):
    endpoint = "https://api.spotify.com/v1/me/player/currently-playing"
    options = {'market' : market}
    ret = spot.get(endpoint, params=options)
    return ret.json()

def status(spot, market='from_token'):
    endpoint = 'https://api.spotify.com/v1/me/player'
    options = {'market' : market}
    ret = spot.get(endpoint, params=options)
    return ret.json()

# Profile
def get_current_profile(spot):
    endpoint = 'https://api.spotify.com/v1/me/'
    ret = spot.get(endpoint)
    return ret.json()
