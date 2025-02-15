from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import re
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# Load credentials from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

def get_playlist_uri_from_link(playlist_link: str) -> str:
    """Get Spotify playlist URI from Spotify playlist link"""
    if match := re.match(r"https://open.spotify.com/playlist/([^?/]+)(?:\?.*)?$", playlist_link):
        return match.groups()[0]
    raise ValueError("Expected format: https://open.spotify.com/playlist/...")

def authenticate():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-playlist', methods=['POST'])
def fetch_playlist():
    try:
        playlist_link = request.json.get('playlist_link')
        if not playlist_link:
            return jsonify({'error': 'No playlist link provided'}), 400

        session = authenticate()
        playlist_uri = get_playlist_uri_from_link(playlist_link)
        tracks = session.playlist_tracks(playlist_uri)['items']

        playlist_tracks = [
            {
                'name': track['track']['name'],
                'artists': ', '.join([artist['name'] for artist in track['track']['artists']])
            }
            for track in tracks
        ]

        return jsonify({'tracks': playlist_tracks})

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)