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
    
    with open('json.txt', 'w') as fh:
        from pprint import pformat
        pretty = pformat(ret.json())
        fh.write(pretty)
    
    return ret.json()

# Album

# Artist

# Playlist

# Track
def get_track(spot, sid):
    endpoint = 'https://api.spotify.com/v1/tracks/'
    ret = spot.get(endpoint+sid)
    return ret.json()

# Player
def play(spot):
    endpoint = 'https://api.spotify.com/v1/me/player/play'
    spot.post(endpoint)
    
def pause(spot):
    endpoint = 'https://api.spotify.com/v1/me/player/pause'
    spot.post(endpoint)
    
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


