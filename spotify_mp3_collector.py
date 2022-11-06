import spotipy
import yt_dlp
from youtube_search import YoutubeSearch
from spotipy.oauth2 import SpotifyOAuth
import os
from decouple import config


def spotify_auth():
    print('Creating client')
    oauth = SpotifyOAuth(client_id=config('CLIENT_ID'),
                         client_secret=config('CLIENT_SECRET'),
                         scope=config('SCOPE'),
                         redirect_uri=config('REDIRECT_URI'))

    sp = spotipy.Spotify(auth_manager=oauth)
    print('Client ready')
    return sp


def get_saved_tracknames(sp, desired_amount=10, offset=0):

    # collect all pages of results from api
    print(f'Collecting your recent saved tracks from spotify')
    spotify_results = sp.current_user_saved_tracks(offset=offset)
    all_track_results = spotify_results['items']

    # ~20 per page
    # load another page of saved songs to reach desired amount
    while spotify_results['next'] and len(all_track_results) < desired_amount:
        spotify_results = sp.next(spotify_results)
        all_track_results.extend(spotify_results['items'])

    # create simple list of artists and tracknames from API results
    tracks = []
    for track_info in all_track_results:
        artist = track_info['track']['artists'][0]['name']
        song_name = track_info['track']['name']
        tracks.append(f'{artist} - {song_name}')

    print(f'Collected {desired_amount} saved tracks')
    return tracks[:desired_amount]


def fetch_URLS_from_tracknames(tracks):
    url_list = []
    BASE = 'https://www.youtube.com'

    print('Fetching youtube URLS from saved songs')

    for track in tracks:
        search_results = YoutubeSearch(track, max_results=1).to_dict()
        SUFFIX = search_results[0].get("url_suffix")
        url = f'{BASE}{SUFFIX}'
        url_list.append(url)

    print('Found youtube URLs for spotify songs')
    return url_list


def download_mp3_from_urls(urls, amount=10):
    output_path = os.path.join(os.getcwd(), "Songs")
    try:
        os.mkdir(output_path)
    except:
        print('Output folder found.')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path + '/%(title)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls[:amount])

    print('Finished')


number_of_songs = 20
offset = 0

client = spotify_auth()
tracks = get_saved_tracknames(
    client, desired_amount=number_of_songs, offset=offset)
urls = fetch_URLS_from_tracknames(tracks)
download_mp3_from_urls(urls, amount=number_of_songs)
