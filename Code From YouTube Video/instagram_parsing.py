import json
import requests
from bs4 import BeautifulSoup

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

post_url = 'https://www.instagram.com/p/By0dag0j4Jc/'

user_data = None
soup = None

# Download the Post HTML doc.
try:
    html_doc = requests.get(post_url)
except requests.RequestException as e:
    print('Unable to get the data of the Post from Instragram!', e)
else:
    # Parse the HTML Doc.
    soup = BeautifulSoup(html_doc.text, 'html.parser')

    for i in soup.find_all('script', type='text/javascript'):
        if i.string.startswith('window._sharedData'):
            data = i.string
            user_data = json.loads(data[21:].strip(';')).get('entry_data')
            break


user_profile = user_data.get('PostPage')[0].get('graphql').get('shortcode_media')

is_video = user_profile.get('is_video')
is_ad = user_profile.get('is_ad')

if is_ad:
    print('Ads or content currently in promotions are not supported!')
else:
    owner = user_profile.get('owner')
    image_url = user_profile.get('display_url')
    video_url = user_profile.get('video_url')
    location = user_profile.get('location')

    if location:
        location = location.get('name')
    else:
        location = ''
    tagged_users = user_profile.get('edge_media_to_tagged_user')

    if tagged_users:
        tagged_users = tagged_users.get('edges')
    else:
        tagged_users = ''

    caption = user_profile.get('edge_media_to_caption')
    if caption:
        caption = caption.get('edges')[0].get('node').get('text').encode('ascii', 'ignore').decode('utf-8')
    else:
        caption = ''

    likes = user_profile.get('edge_media_preview_like')
    if likes:
        likes = likes.get('count')
    else:
        likes = 0

    comments = user_profile.get('edge_media_to_parent_comment')
    if comments:
        comments = comments.get('count')
    else:
        comments = ''

    is_video = user_profile.get('is_video')
    is_ad = user_profile.get('is_ad')

    print('Owner:')
    print('    Full name:', owner.get('full_name'))
    print('    Username:', owner.get('username'))
    print('    ID:', owner.get('id'))
    print('    Profile Pic URL:', owner.get('profile_pic_url'))
    print()
    print('Image URL:', image_url)
    print()
    if is_video:
        print('Video URL:', video_url)
        print()
    print('Location:', location)
    print()
    print('Tagged Users:', [i.get('node').get('user').get('username') for i in tagged_users])
    print()
    print('Caption:', caption)
    print()
    print('Likes:', likes)
    print()
    print('Is Video:', is_video)
    print()
    print('Is Ad:', is_ad)
    print()
    print('Comments:', comments)

    # Get Hashtags
    if is_video:
        hashtags = soup.find_all('meta', property='video:tag')
    else:
        hashtags = soup.find_all('meta', property='instapp:hashtags')

    # Print a count of Hashtags
    print('Hashtags Count:', len(hashtags))
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # Print each Hashtag.
    for hashtag in hashtags:
        print('#' + hashtag['content'])

    # Download Photo
    photo = requests.get(image_url)
    f = open(image_url.split('?')[0].split('/')[-1], 'wb')
    f.write(photo.content)
    f.close()

    # Download Video
    if is_video:
        video = requests.get(video_url)
        f = open(video_url.split('?')[0].split('/')[-1], 'wb')
        f.write(video.content)
        f.close()
