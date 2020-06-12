import json
import requests
import re
import os

username = 'thephotoadventure'

path = os.path.join(f'media_data_for_{username}/')
os.mkdir(path) if not os.path.isdir(path) else None
match = re.compile(r'/(?P<filename>[\w_]+\.[\w]{3,4})\?')

with open(f'user_profile_data_{username}.json', 'r') as f:
    data = json.load(f)

for post in data['graphql']['user']['edge_owner_to_timeline_media']['edges']:
    if post['node']['is_video'] is False:
        media_url = post['node']['display_url']
        filename = match.search(media_url)
        if filename:
            photo = requests.get(media_url)
            f = open(os.path.join(path, filename.group('filename')), 'wb')
            f.write(photo.content)
            f.close()
        if post['node'].get('edge_sidecar_to_children') is not None:
            for sub_image in post['node']['edge_sidecar_to_children']['edges']:
                media_url = sub_image['node']['display_url']
                filename = match.search(media_url)
                if filename:
                    photo = requests.get(media_url)
                    f = open(os.path.join(path, filename.group('filename')), 'wb')
                    f.write(photo.content)
                    f.close()
    elif post['node']['is_video'] is True:
        media_url = post['node']['video_url']
        filename = match.search(media_url)
        if filename:
            video = requests.get(media_url)
            f = open(os.path.join(path, filename.group('filename')), 'wb')
            f.write(video.content)
            f.close()
