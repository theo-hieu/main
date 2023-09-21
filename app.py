from flask import Flask, request, url_for, session, redirect
#get data from request, get urls, talk to spotify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import pandas as pd

app = Flask(__name__)
#py -m flask run
app.secret_key = "34920ioae"
app.config['SESSION_COOKIE_NAME'] = 'SessionObj'#store data about user session
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth() #create oauth obj
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        redirect(url_for("login", _external=False))
    sp = spotipy.Spotify(auth = token_info['access_token'])
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        if (len(curGroup) < 50):
            break
    df = pd.DataFrame(results, columns = ["song names"])
    print(df)
    return "done"

def get_token():
    token_info = session.get(TOKEN_INFO, None) #get token if it exists
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = "id",
        client_secret = "secret",
        redirect_uri = url_for('redirectPage', _external=True),
        scope = "user-library-read")
