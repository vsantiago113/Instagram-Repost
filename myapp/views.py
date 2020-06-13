from myapp import application
from flask import render_template, redirect, url_for, request, flash
import json
import os
from collections import namedtuple
import requests
import re


@application.route('/')
def home():
    os.mkdir('myapp/data') if not os.path.isdir('myapp/data') else None
    os.mkdir('myapp/data/cashed') if not os.path.isdir('myapp/data/cashed') else None

    Profile = namedtuple('Profile', 'username img')
    history = []
    for i in os.listdir('myapp/data/cashed'):
        with open(f'myapp/data/cashed/{i}') as f:
            data = json.load(f)
        history.append(Profile(username=data['username'],
                               img=data['image']))
    return render_template('index.html', history=history)


@application.route('/user-profile/<username>/<history>/<has_next_page>/<end_cursor>', defaults={'username': None,
                                                                                                'history': None,
                                                                                                'has_next_page': None,
                                                                                                'end_cursor': None},
                   methods=['GET', 'POST'])
@application.route('/user-profile/<username>/<history>/<has_next_page>/<end_cursor>', defaults={'has_next_page': None,
                                                                                                'end_cursor': None},
                   methods=['GET', 'POST'])
@application.route('/user-profile/<username>/<history>/<has_next_page>/<end_cursor>', methods=['GET', 'POST'])
def user_profile(username, history, has_next_page, end_cursor):
    if history.lower() == 'true':
        with open(f'myapp/data/cashed/{username}.json') as f:
            cashed_data = json.load(f)

        r = requests.get(f'https://instagram.com/{cashed_data["username"]}/?__a=1')
        user_data = r.json()

        r = requests.get('https://instagram.com/graphql/query', params={'query_hash': cashed_data['posts'],
                                                                        'id': cashed_data['id'],
                                                                        'first': 24
                                                                        }
                         )
        user_posts = r.json()

        has_next_page = str(user_posts['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'])
        if has_next_page.lower() == 'true':
            pagination = True
            end_cursor = user_posts['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        else:
            pagination = None
            end_cursor = None
    elif has_next_page.lower() == 'true':
        with open(f'myapp/data/cashed/{username}.json') as f:
            cashed_data = json.load(f)

        r = requests.get(f'https://instagram.com/{cashed_data["username"]}/?__a=1')
        user_data = r.json()

        r = requests.get('https://instagram.com/graphql/query', params={'query_hash': cashed_data['posts'],
                                                                        'id': cashed_data['id'],
                                                                        'first': 24,
                                                                        'after': end_cursor
                                                                        }
                         )
        user_posts = r.json()

        has_next_page = str(user_posts['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'])
        if has_next_page.lower() == 'true':
            pagination = True
            end_cursor = user_posts['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        else:
            pagination = None
            end_cursor = None
    else:
        if request.method == 'POST':
            username = request.form['username']
            r = requests.get(f'https://instagram.com/{username}/?__a=1')
            user_data = r.json()
            if user_data:
                r = requests.get(f'https://instagram.com/{username}')
                js_file_posts = re.search(r'static/bundles/(metro|es6)/ProfilePageContainer.js/\w+.js', r.text)
                js_file_post = re.search(r'static/bundles/(metro|es6)/Consumer.js/\w+.js', r.text)

                r = requests.get(f'https://instagram.com/{js_file_posts.group()}')
                query_hash_posts = re.search(
                    r'profilePosts.byUserId.get\(n\)\)\|\|void 0===\w\?void 0:\w.pagination},queryId:\"(?P<queryId>\w+)\"',
                    r.text)

                r = requests.get(f'https://instagram.com/{js_file_post.group()}')
                query_hash_post = re.search(
                    r'actionHandler:.*Object.defineProperty\(e,\'__esModule\',{value:!0}\);(const|var) \w=\"(?P<queryId>\w+)\"',
                    r.text)

                data = {'username': user_data['graphql']['user']['username'],
                        'id': user_data['graphql']['user']['id'],
                        'image': user_data['graphql']['user']['profile_pic_url'],
                        'posts': query_hash_posts.group("queryId"),
                        'post': query_hash_post.group("queryId")}

                with open(f'myapp/data/cashed/{username}.json', 'w') as f:
                    json.dump(data, f)

                r = requests.get('https://instagram.com/graphql/query', params={'query_hash': query_hash_posts.group("queryId"),
                                                                                'id': user_data['graphql']['user']['id'],
                                                                                'first': 24,
                                                                                }
                                 )
                user_posts = r.json()

                has_next_page = str(user_posts['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'])
                if has_next_page.lower() == 'true':
                    pagination = True
                    end_cursor = user_posts['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                else:
                    pagination = None
                    end_cursor = None
            else:
                flash('No user account found!')
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))

    return render_template('user_profile.html', user_data=user_data, user_posts=user_posts, pagination=pagination,
                           end_cursor=end_cursor, username=username)


@application.route('/post/<username>/<shortcode>', methods=['GET', 'POST'])
def post(username, shortcode):
    with open(f'myapp/data/cashed/{username}.json') as f:
        cashed_data = json.load(f)
    r = requests.get('https://instagram.com/graphql/query', params={'query_hash': cashed_data['post'],
                                                                    'shortcode': shortcode,
                                                                    'child_comment_count': 3,
                                                                    'fetch_comment_count': 40,
                                                                    }
                     )
    if r.json():
        return render_template('post.html', data=r.json())
    else:
        flash('Post was not found!')
        return render_template('post.html', data=None)


@application.route('/repost/<username>/<shortcode>')
def repost(username, shortcode):
    with open(f'myapp/data/cashed/{username}.json') as f:
        cashed_data = json.load(f)
    r = requests.get('https://instagram.com/graphql/query', params={'query_hash': cashed_data['post'],
                                                                    'shortcode': shortcode,
                                                                    'child_comment_count': 3,
                                                                    'fetch_comment_count': 40,
                                                                    }
                     )
    print(json.dumps(r.json(), indent=4))
    post = r.json()['data']['shortcode_media']
    if post['is_video']:
        post_media = [post['video_url']]
    else:
        post_media = []
        if post.get('edge_sidecar_to_children') is not None:
            for sub_image in post['edge_sidecar_to_children']['edges']:
                media_url = sub_image['node']['display_url']
                post_media.append(media_url)
        else:
            post_media = [post['display_url']]

    post_tagged_users = []
    for i in post['edge_media_to_tagged_user']['edges']:
        post_tagged_users.append(i['node']['user']['username'])
    for i in re.findall(r'[@][\w\-.]+', post['edge_media_to_caption']['edges'][0]['node']['text'].replace('\n', ' ')):
        post_tagged_users.append(i.strip('@'))
    post_tagged_users = list(set(post_tagged_users))
    post_hash_tags = re.findall(r'[#][\w\-.]+', post['edge_media_to_caption']['edges'][0]['node']['text'].replace('\n', ' '))
    post_hash_tags = list(set(post_hash_tags))
    if post.get('location'):
        post_location = post['location']['name']
    else:
        post_location = ''
    post_caption = post['edge_media_to_caption']['edges'][0]['node']['text'].replace('\n', '<br />')

    return render_template('repost.html', post_media=post_media, post_tagged_users=post_tagged_users,
                           post_hash_tags=post_hash_tags, post_location=post_location, post_caption=post_caption)
