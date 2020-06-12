from myapp import application
from flask import render_template, redirect, url_for
import json
import os
from collections import namedtuple


@application.route('/')
def home():
    Profile = namedtuple('Profile', 'username img')
    history = []
    for i in os.listdir('data/user_profiles'):
        with open(f'data/user_profiles/{i}') as f:
            data = json.load(f)
        history.append(Profile(username=data['graphql']['user']['username'],
                               img=data['graphql']['user']['profile_pic_url']))
    return render_template('index.html', history=history)
