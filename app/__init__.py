from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

cache = redis.from_url('redis://localhost:6379', encoding='utf-8',
                       decode_responses=True)

login_manager = LoginManager()
login_manager.init_app(app)

from app import views, api # noqa
