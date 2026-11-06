"""
The flask application package.
"""
import logging
import sys
from flask import Flask
from flask.logging import default_handler
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)

# Azure App Service terminates TLS in a front-end proxy; trust its X-Forwarded-* headers
# so url_for(..., _external=True) builds correct https URLs (needed for the MSAL redirect URI).
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Logging: send INFO+ messages to stdout so they show up in the App Service "Log stream"
# (and in the terminal when running locally).
app.logger.setLevel(logging.INFO)
app.logger.removeHandler(default_handler)  # avoid duplicated lines (stderr + stdout)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))
app.logger.addHandler(streamHandler)
app.logger.propagate = False

Session(app)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

import FlaskWebProject.views
