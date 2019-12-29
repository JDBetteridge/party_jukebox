import os

import jukebox_queue as jq
import spotify_api as sa

from flask import (Flask, request, render_template,
                    make_response,
                    redirect, url_for, session)
from requests_oauthlib import OAuth2Session
from random import sample, choices
from threading import Timer

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
obj = sa.spotify_auth.auth( jukebox,
                            client,
                            scope=[ 'user-read-private',
                                    'user-modify-playback-state',
                                    'user-read-currently-playing',
                                    'playlist-read-private',
                                    'playlist-modify-public'])

# Setup global queue
QUEUE = jq.Queue()
PLAY_THREAD = None

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
            spot = OAuth2Session(CID, token=AUTH)
            try:
                current = sa.get_current(spot)
                queue = QUEUE
                resp = render_template('playlist.html',
                                        user=user,
                                        queue=queue,
                                        progress=current['progress_ms'])
            except:
                queue = jq.Queue([jq.default_entry]) + QUEUE
                resp = render_template('playlist.html', user=user, queue=queue)
            
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
        if admin:
            resp = make_response(redirect('/select_playlist'))
        else:
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

@jukebox.route('/select_playlist', methods=['GET', 'POST'])
def select_playlist():
    spot = OAuth2Session(CID, token=AUTH)
    if request.method == 'POST':
        string = request.form['string']
        sa.create_playlist(spot, name=string)
        resp = redirect('/search')
    else:
        json = sa.get_users_playlists(spot)
        resp = render_template('select_playlist.html', playlists=json)
    
    return resp

@jukebox.route('/load_playlist/<pid>')
def load_playlist(pid):
    global PLAY_THREAD
    spot = OAuth2Session(CID, token=AUTH)
    json = sa.get_playlist_tracks(spot, pid)
    rand_id = choices(range(json['total']), k=11)
    for idx in rand_id:
        sid = json['items'][idx]['track']['id']
        track = sa.get_track(spot, sid)
        QUEUE.add('Auto', track)
    
    if PLAY_THREAD is None:
        sa.play(spot, uris=[QUEUE[0].uri])
        time_sec = QUEUE[0].duration/1000
        PLAY_THREAD = Timer(time_sec, play_next)
        PLAY_THREAD.start()
    return redirect('/')

def play_next():
    spot = OAuth2Session(CID, token=AUTH)
    QUEUE.pop(0)
    sa.play(spot, uris=[QUEUE[0].uri])
    time_sec = QUEUE[0].duration/1000
    PLAY_THREAD = Timer(time_sec, play_next)
    PLAY_THREAD.start()

@jukebox.route('/'+secret_user)
def admin_user():
    return render_template('controls.html', user=session['user'], queue=QUEUE)

@jukebox.route('/info')
def info():
    spot = OAuth2Session(CID, token=AUTH)
    return sa.get_users_playlists(spot)

@jukebox.route('/playlist/<pid>')
def playlist(pid):
    spot = OAuth2Session(CID, token=AUTH)
    return sa.get_playlist_tracks(spot, pid)

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

@jukebox.route('/test_play/<uri>')
def tplay(sid):
    # http://127.0.0.1:6500/test_play/spotify:track:5vJtCjdjiyF6uRKZvbWfHv
    spot = OAuth2Session(CID, token=AUTH)
    th = Timer(10.0, sa.play, args=(spot, ), kwargs={'uris':[uri]})
    th.start()
    return redirect('/')

@jukebox.route('/action/<x>', defaults={'dest' : 'index'})
@jukebox.route('/action/<x>/<dest>')
def action(x, dest='index'):
    global AUTH, CID
    try:
        spot = OAuth2Session(CID, token=AUTH)
    except KeyError:
        return redirect('/obtain_token')
    call = getattr(sa, x)
    call(spot)
    return redirect(url_for(dest))
    
@jukebox.route('/queue/<user>/<sid>')
def queue(user, sid):
    global AUTH, CID, QUEUE
    try:
        spot = OAuth2Session(CID, token=AUTH)
    except KeyError:
        return redirect('/obtain_token')
    print(user, ':', sid)
    json = sa.get_track(spot, sid)
    QUEUE.add(user, json)
    QUEUE.sort()
    return redirect('/')

@jukebox.route('/vote/<user>/<int:idx>/<updown>')
def vote(user, idx, updown):
    global QUEUE
    if updown == '+':
        QUEUE[idx].upvote(user)
        QUEUE.sort()
    elif updown == '-':
        QUEUE[idx].downvote(user)
        QUEUE.sort()
    else:
        pass
    # print(user, ':', idx, ':', updown)
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
