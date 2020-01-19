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
SPOT = None
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
PLAYLIST = None

@jukebox.route('/')
def index():
    '''
    Index of jukebox, shows current playing song and queue
    '''
    global SPOT
    if SPOT is None:
        resp = redirect('/setup')
    else:
        # If cookie exists, it gets returned
        try:
            user = request.cookies['user']
            session['user'] = user
            try:
                current = sa.get_current(SPOT)
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
    global SPOT
    if request.method == 'POST':
        username = request.form['user']
        if username.strip() == '':
            mesg = 'Try entering a username with printing characters'
            resp = make_response(render_template('login.html', info=mesg))
        elif admin:
            resp = make_response(redirect('/select_playlist'))
        else:
            resp = make_response(redirect('/'))
        session['user'] = username
        resp.set_cookie('user', username)
    else:
        if admin:
            extra = {   'client_id' : client.id,
                        'client_secret' : client.secret}
            saver = lambda tok : session.update({'oauth_token' : tok})
            SPOT = OAuth2Session(   client.id,
                                    token=session['oauth_token'],
                                    auto_refresh_url=sa.spotify_auth.spotify_token,
                                    auto_refresh_kwargs=extra,
                                    token_updater=saver)
            mesg = 'You are the session admin, use code '
            mesg += secret_user
            mesg += ' to log in to admin account'
        else:
            mesg = ''
        resp = render_template('login.html', info=mesg)
    return resp

@jukebox.route('/select_playlist', methods=['GET', 'POST'])
def select_playlist():
    global SPOT
    if request.method == 'POST':
        string = request.form['string']
        if string.strip() == '':
            resp = redirect('/select_playlist')
        else:
            sa.create_playlist(SPOT, name=string)
            resp = redirect('/search')
    else:
        json = sa.get_users_playlists(SPOT)
        resp = render_template('select_playlist.html', playlists=json)
    
    return resp

@jukebox.route('/load_playlist/<pid>')
def load_playlist(pid):
    global PLAY_THREAD, SPOT, PLAYLIST
    PLAYLIST = pid
    json = sa.get_playlist_tracks(SPOT, PLAYLIST)
    rand_id = choices(range(json['total']), k=11)
    for idx in rand_id:
        sid = json['items'][idx]['track']['id']
        track = sa.get_track(SPOT, sid)
        QUEUE.add('Auto', track)
    
    if PLAY_THREAD is None:
        sa.play(SPOT, uris=[QUEUE[0].uri])
        time_sec = QUEUE[0].duration/1000
        PLAY_THREAD = Timer(time_sec, play_next)
        PLAY_THREAD.start()
    return redirect('/')

def random_selection():
    global SPOT, PLAYLIST, QUEUE
    json = sa.get_playlist_tracks(SPOT, PLAYLIST)
    rand_id = choices(range(json['total']), k=11)
    for idx in rand_id:
        sid = json['items'][idx]['track']['id']
        track = sa.get_track(SPOT, sid)
        QUEUE.add('Auto', track)

def play_next():
    global SPOT, PLAY_THREAD
    QUEUE.pop(0)
    while skip_criterion(QUEUE[0]):
        QUEUE.pop(0)
        if len(QUEUE) == 0:
            break
    
    if len(QUEUE) == 0:
        random_selection()
        
    sa.play(SPOT, uris=[QUEUE[0].uri])
    time_sec = QUEUE[0].duration/1000
    PLAY_THREAD.cancel()
    PLAY_THREAD = Timer(time_sec, play_next)
    PLAY_THREAD.start()

@jukebox.route('/'+secret_user)
def admin_user():
    global SPOT
    current = sa.get_current(SPOT)
    return render_template('controls.html',
                            user=session['user'],
                            queue=QUEUE,
                            progress=current['progress_ms'])

@jukebox.route('/info')
def info():
    global SPOT
    return sa.get_users_playlists(SPOT)

@jukebox.route('/playlist/<pid>')
def playlist(pid):
    global SPOT
    return sa.get_playlist_tracks(SPOT, pid)

@jukebox.route('/search', methods=['GET', 'POST'])
def search():
    '''
    Finding new songs
    '''
    global SPOT
    if request.method == 'POST':
        string = request.form['string']
        qtype = []
        for key in ['track', 'artist', 'album', 'playlist']:
            if request.form.get(key, '') == 'on':
                qtype.append(key)
        if string.strip() == '':
            qtype = []
        
        results = sa.search(SPOT, string, qtype)
        qtype = [item+'s' for item in qtype]
        resp = render_template( 'search_results.html',
                                user=session['user'],
                                qtype=qtype,
                                results=results)
    else:
        resp = render_template('search.html', user=session['user'])
    return resp

@jukebox.route('/more', methods=['GET', 'POST'])
def more_results():
    global SPOT
    if request.method == 'POST':
        qtype = [request.form['qtype']]
        url = request.form['url']
        results = SPOT.get(url).json()
        resp = render_template( 'search_results.html',
                                    user=session['user'],
                                    qtype=qtype,
                                    results=results)
    else:
        resp = 'This string'
    return resp
    

@jukebox.route('/search/<qtype>/<iid>')
def search_more(qtype, iid):
    global SPOT
    if qtype == 'artists':
        results = sa.get_artist_top_tracks(SPOT, aid=iid)
    elif qtype == 'albums':
        results = sa.get_album_tracks(SPOT, aid=iid)
    elif qtype == 'playlists':
        results = sa.get_playlist_tracks(SPOT, pid=iid)
    resp = render_template( 'search_results_more.html',
                                user=session['user'],
                                qtype=[qtype],
                                results=results)
    return resp

@jukebox.route('/test_play/<uri>')
def tplay(sid):
    # http://127.0.0.1:6500/test_play/spotify:track:5vJtCjdjiyF6uRKZvbWfHv
    global SPOT
    th = Timer(10.0, sa.play, args=(SPOT, ), kwargs={'uris':[uri]})
    th.start()
    return redirect('/')

@jukebox.route('/action/<x>', defaults={'dest' : 'index'})
@jukebox.route('/action/<x>/<dest>')
def action(x, dest='index'):
    global SPOT, PLAY_THREAD
    
    # ~ call = getattr(sa, x)
    # ~ call(SPOT)
    
    if x == 'pause':
        PLAY_THREAD.cancel()
        sa.pause(SPOT)
    elif x == 'play':
        sa.play(SPOT)
        current = sa.get_current(SPOT)['progress_ms']
        time_sec = (QUEUE[0].duration - current)/1000
        PLAY_THREAD = Timer(time_sec, play_next)
        PLAY_THREAD.start()
    elif x == 'previous':
        sa.play(SPOT, uris=[QUEUE[0].uri])
        time_sec = QUEUE[0].duration/1000
        PLAY_THREAD.cancel()
        PLAY_THREAD = Timer(time_sec, play_next)
        PLAY_THREAD.start()
    elif x == 'skip':
        # Play next already cancels timer
        play_next()
    
    return redirect(url_for(dest))
    
@jukebox.route('/queue/<user>/<sid>')
def queue(user, sid):
    global SPOT, QUEUE
    print(user, ':', sid)
    json = sa.get_track(SPOT, sid)
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
        if idx == 0 and skip_criterion(QUEUE[0]):
            play_next()
    else:
        pass
    # print(user, ':', idx, ':', updown)
    return redirect('/')

def skip_criterion(entry):
    ''' Proportion of votes needed for current song to be skipped
    '''
    u = max(1, entry.ups)
    d = entry.downs
    factor = 1.5
    return d >= factor*u

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
