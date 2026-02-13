import requests
import json
import os
from dotenv import load_dotenv
from urllib3 import response

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")

CHANNEL_NAME = "MrBeast"

MAX_RESULTS = 50

url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_NAME}&key={API_KEY}'

def get_playlist_id():
    try:
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()
        
        #print(json.dumps(data, indent=4))

        channel_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        print(channel_playlist_id)
    
        return channel_playlist_id
    
    except requests.exceptions.RequestException as e:
        raise e



def get_video_ids():
    playlist_id = get_playlist_id()
    video_ids = []

    next_page_token = ""
    while True:
        base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={playlist_id}&key={API_KEY}'
        try:
            if next_page_token != "":
                base_url += f'&pageToken={next_page_token}'
            response = requests.get(base_url)

            response.raise_for_status()

            data = response.json()
            for item in data.get("items",[]):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)
            if data.get("nextPageToken") is not None:
                next_page_token = data.get("nextPageToken")
            else:
                break

        except requests.exceptions.RequestException as e:
            raise e

    print(len(video_ids))
    print(video_ids)

if __name__ == "__main__":
    get_video_ids()
