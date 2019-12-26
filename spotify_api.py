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

# Player
def skip(spot):
    endpoint = 'https://api.spotify.com/v1/me/player/next'
    spot.post(endpoint)
