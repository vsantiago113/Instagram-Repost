import requests
import json
import re

ig_url = 'https://instagram.com'
ig_username = 'thephotoadventure'
query_url = f'{ig_url}/graphql/query'
all_user_posts = []

r = requests.get(f'{ig_url}/{ig_username}/?__a=1')
all_data = r.json()

user_data = all_data['graphql']['user']
user_posts = user_data['edge_owner_to_timeline_media']
end_cursor = user_posts['page_info']['end_cursor']
has_next = user_posts['page_info']['has_next_page']
user_id = user_data['id']

all_user_posts.extend(user_posts['edges'])

if has_next is True:
    r = requests.get(f'{ig_url}/{ig_username}')
    js_file_posts = re.search(r'/static/bundles/(metro|es6)/ProfilePageContainer.js/\w+.js', r.text)
    js_file_comments = re.search(r'/static/bundles/(metro|es6)/Consumer.js/\w+.js', r.text)

    r = requests.get(f'{ig_url}{js_file_posts.group()}')
    query_hash_posts = re.search(
        r'profilePosts.byUserId.get\(n\)\)\|\|void 0===\w\?void 0:\w.pagination},queryId:\"(?P<queryId>\w+)\"',
        r.text)

    r = requests.get(f'{ig_url}{js_file_comments.group()}')
    query_hash_comments = re.search(
        r'actionHandler:.*Object.defineProperty\(e,\'__esModule\',{value:!0}\);(const|var) \w=\"(?P<queryId>\w+)\"',
        r.text)

    while end_cursor is not None or has_next is True:
        # Get posts and pagination for loading more
        r = requests.get(query_url, params={'query_hash': query_hash_posts.group('queryId'),
                                            'id': user_id,
                                            'first': 100,
                                            'after': end_cursor
                                            }
                         )
        user_data = r.json()['data']['user']
        user_posts = user_data['edge_owner_to_timeline_media']
        end_cursor = user_posts['page_info']['end_cursor']
        has_next = user_posts['page_info']['has_next_page']

        all_user_posts.extend(user_posts['edges'])

    # Get newest post and pull details with comments
    newest_post = user_posts['edges'][0]
    if newest_post:
        r = requests.get(query_url, params={'query_hash': query_hash_comments.group('queryId'),
                                            'shortcode': newest_post['node']['shortcode'],
                                            'child_comment_count': 3,
                                            'fetch_comment_count': 40,
                                            }
                         )
        print(json.dumps(r.json(), indent=4))

all_data['graphql']['user']['edge_owner_to_timeline_media']['edges'] = all_user_posts

with open(f'user_profile_data_{ig_username}.json', 'w') as f:
    json.dump(all_data, f)
