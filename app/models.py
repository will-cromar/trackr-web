from datetime import datetime

from app import db
import flask_login


class Movie(db.Model):
    media_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    time = db.Column(db.DateTime)
    author = db.Column(db.String(20))

    @property
    def delta(self):
        return self.time - datetime.utcnow()


class User(db.Model, flask_login.UserMixin):
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(100))

    def get_id(self):
        return self.username
