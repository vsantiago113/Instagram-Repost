from myapp import application
from flask import render_template, redirect, url_for, request, flash, send_file
import json
import os
from collections import namedtuple
import requests
import re


# @application.route('/')
# def home():
#     Profile = namedtuple('Profile', 'username img')
#     history = []
#     for i in os.listdir('myapp/data/user_profiles'):
#         with open(f'myapp/data/user_profiles/{i}') as f:
#             data = json.load(f)
#         history.append(Profile(username=data['graphql']['user']['username'],
#                                img=data['graphql']['user']['profile_pic_url']))
#     return render_template('index.html', history=history)

@application.route('/')
def home():
    Profile = namedtuple('Profile', 'username img')
    history = []
    for i in os.listdir('myapp/data/cashed'):
        with open(f'myapp/data/cashed/{i}') as f:
            data = json.load(f)
        history.append(Profile(username=data['username'],
                               img=data['image']))
    return render_template('index.html', history=history)


@application.route('/user-profile/<username>/<history>', defaults={'username': None, 'history': None},
                   methods=['GET', 'POST'])
@application.route('/user-profile/<username>/<history>', methods=['GET', 'POST'])
def user_profile(username, history):
    if history.lower() == 'true':
        with open(f'myapp/data/cashed/{username}.json') as f:
            cashed_data = json.load(f)

        r = requests.get(f'https://instagram.com/{cashed_data["username"]}/?__a=1')
        all_data = r.json()
    else:
        if request.method == 'POST':
            username = request.form['username']
            r = requests.get(f'https://instagram.com/{username}/?__a=1')
            all_data = r.json()
            if all_data:
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

                data = {'username': all_data['graphql']['user']['username'],
                        'image': all_data['graphql']['user']['profile_pic_url'],
                        'posts': query_hash_posts.group("queryId"),
                        'post': query_hash_post.group("queryId")}

                with open(f'myapp/data/cashed/{username}.json', 'w') as f:
                    json.dump(data, f)
            else:
                flash('No user account found!')
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))

    return render_template('user_profile.html', data=all_data)


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


@application.route('/save_media/<url>')
def save_media(url):
    return send_file(url, as_attachment=True)


# @application.route('/user-profile/<username>/<history>', defaults={'username': None, 'history': None},
#                    methods=['GET', 'POST'])
# @application.route('/user-profile/<username>/<history>', methods=['GET', 'POST'])
# def user_profile(username, history):
#     if history.lower() == 'true':
#         if os.path.isfile(f'myapp/data/user_profiles/user_profile_data_{username}.json'):
#             with open(f'myapp/data/user_profiles/user_profile_data_{username}.json') as f:
#                 data = json.load(f)
#     else:
#         if request.method == 'POST':
#             username = request.form['username']
#             ig_url = 'https://instagram.com'
#             ig_username = username
#             query_url = f'{ig_url}/graphql/query'
#             all_user_posts = []
#
#             r = requests.get(f'{ig_url}/{ig_username}/?__a=1')
#             all_data = r.json()
#
#             if all_data:
#                 user_data = all_data['graphql']['user']
#                 user_posts = user_data['edge_owner_to_timeline_media']
#                 end_cursor = user_posts['page_info']['end_cursor']
#                 has_next = user_posts['page_info']['has_next_page']
#                 user_id = user_data['id']
#
#                 all_user_posts.extend(user_posts['edges'])
#
#                 if has_next is True:
#                     r = requests.get(f'{ig_url}/{ig_username}')
#                     js_file_posts = re.search(r'/static/bundles/(metro|es6)/ProfilePageContainer.js/\w+.js', r.text)
#                     js_file_post = re.search(r'/static/bundles/(metro|es6)/Consumer.js/\w+.js', r.text)
#
#                     r = requests.get(f'{ig_url}{js_file_posts.group()}')
#                     query_hash_posts = re.search(
#                         r'profilePosts.byUserId.get\(n\)\)\|\|void 0===\w\?void 0:\w.pagination},queryId:\"(?P<queryId>\w+)\"',
#                         r.text)
#
#                     r = requests.get(f'{ig_url}{js_file_post.group()}')
#                     query_hash_post = re.search(
#                         r'actionHandler:.*Object.defineProperty\(e,\'__esModule\',{value:!0}\);(const|var) \w=\"(?P<queryId>\w+)\"',
#                         r.text)
#
#                     all_data['query_hash'] = {'posts': query_hash_posts.group('queryId'), 'post': query_hash_post.group('queryId')}
#
#                     while end_cursor is not None or has_next is True:
#                         r = requests.get(query_url, params={'query_hash': query_hash_posts.group('queryId'),
#                                                             'id': user_id,
#                                                             'first': 100,
#                                                             'after': end_cursor
#                                                             }
#                                          )
#                         user_data = r.json()['data']['user']
#                         user_posts = user_data['edge_owner_to_timeline_media']
#                         end_cursor = user_posts['page_info']['end_cursor']
#                         has_next = user_posts['page_info']['has_next_page']
#
#                         all_user_posts.extend(user_posts['edges'])
#
#                     all_data['graphql']['user']['edge_owner_to_timeline_media']['edges'] = all_user_posts
#
#                     with open(f'myapp/data/user_profiles/user_profile_data_{ig_username}.json', 'w') as f:
#                         json.dump(all_data, f)
#
#                     data = all_data
#             else:
#                 flash('No user account found!')
#                 return redirect(url_for('home'))
#         else:
#             return redirect(url_for('home'))
#
#     return render_template('user_profile.html', data=data)
