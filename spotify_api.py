import os
import requests

import spotify_auth

def skip(spot):
    endpoint = 'https://api.spotify.com/v1/me/player/next'
    spot.post(endpoint)
