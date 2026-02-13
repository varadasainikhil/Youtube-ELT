import requests
import json
import os
from dotenv import load_dotenv
from urllib3 import response
from datetime import date

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



def get_video_ids(playlist_id):
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

    return video_ids

def extract_video_data(video_id_list):
    extracted_video_data = []

    def batch_lists(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id: video_id + batch_size]

    try:
        for batch in batch_lists(video_id_list, MAX_RESULTS):
            concatenated_video_id_string = ",".join(batch)
            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={concatenated_video_id_string}&key={API_KEY}'

            response = requests.get(url)

            response.raise_for_status()

            video_object = {}

            data = response.json()

            for item in data.get("items", []):
                video_object["video_id"] = item["id"]
                video_object["title"] = item["snippet"]["title"]
                video_object["publishedAt"] = item["snippet"]["publishedAt"]
                video_object["duration"] = item["contentDetails"]["duration"]
                video_object["viewCount"] = item["statistics"].get("viewCount", None)
                video_object["likeCount"] = item["statistics"].get("likeCount", None)
                video_object["commentCount"] = item["statistics"].get("commentCount", None)

                extracted_video_data.append(video_object)

        return extracted_video_data
    except requests.exceptions.RequestException as e:
        raise e


def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"
    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4,ensure_ascii=False)


if __name__ == "__main__":
    playlist_id = get_playlist_id()
    videos_id = get_video_ids(playlist_id)
    video_data = extract_video_data(videos_id)
    save_to_json(videos_id)