from flask import Flask

application = Flask(__name__)
application.secret_key = 'mysupersecretkey'

import myapp.views
