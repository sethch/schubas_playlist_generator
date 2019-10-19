import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy import util
# Define your username, playlist_id, client_id and client_secret in a config.py file
import config

username = config.spotify_username
playlist_id = config.spotify_playlist_id
client_id = config.spotify_client_id
client_secret = config.spotify_client_secret


def main():
    print('Welcome to Seth\'s Schuba\'s Spotify playlist generator!')
    artists = getArtists()
    makePlaylist(artists)


def authorize():
    scope = 'playlist-modify-private playlist-modify-public playlist-read-private'
    redirect_uri = 'http://localhost:4200/callback'
    return util.prompt_for_user_token(username=username, scope=scope, client_id=client_id,
                                      client_secret=client_secret,
                                      redirect_uri=redirect_uri)


def getArtists():
    artists = set()
    url = 'https://lh-st.com/?pag=1'
    page = requests.get(url)
    print('Parsing results from URL: ' + url)
    soup = BeautifulSoup(page.text, 'html.parser')
    cards = soup.find(class_='card-deck')
    show_list_bodies = cards.find_all('div', class_='card-body')
    for show in show_list_bodies:
        artist_name = show.find('h4')
        if artist_name:
            artists.add(artist_name.text)
    print('Artists: ' + repr(artists) + '\nSize: ' + str(len(artists)))
    return artists


def makePlaylist(artists):
    token = authorize()
    sp = spotipy.Spotify(auth=token)
    sp.user_playlist_replace_tracks(user=username, playlist_id=playlist_id, tracks=[])
    for artist in artists:
        result = sp.search(q=artist, type='artist')
        artist_list = result.get('artists').get('items')
        if artist_list:
            artist_id = artist_list[0].get('id')
            top_tracks = dict(sp.artist_top_tracks(artist_id))
            top_three_tracks = top_tracks.get('tracks')[0:3]
            tracks = []
            for track in top_three_tracks:
                tracks.append(track.get('id'))
            if tracks:
                sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=tracks)


if __name__ == "__main__":
    main()

