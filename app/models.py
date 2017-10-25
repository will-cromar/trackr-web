from datetime import datetime

from app import db
import flask_login


class Listing(db.Model):
    __tablename__ = 'listing'

    listing_id = db.Column('listing_id', db.String(16), nullable=False, primary_key=True)
    title = db.Column('title', db.String(128), nullable=False)
    description = db.Column('description', db.String(4096))
    release_date = db.Column('release_date', db.Date)

    @property
    def delta(self):
        return self.time - datetime.utcnow()

class Person(db.Model):
    __tablename__ = 'person'

    person_id = db.Column('person_id', db.String(16), nullable=False, primary_key=True)
    name = db.Column('name', db.String(128), nullable=False)

class Listing_Writers(db.Model):
    __tablename__ = 'listing_writers'

    listing_id = db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id'), nullable=False, primary_key=True)
    person_id = db.Column('person_id', db.String(16), db.ForeignKey('person.person_id'), nullable=False, primary_key=True)

class Listing_Directors(db.Model):
    __tablename__ = 'listing_directors'

    listing_id = db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id'), nullable=False, primary_key=True)
    person_id = db.Column('person_id', db.String(16), db.ForeignKey('person.person_id'), nullable=False, primary_key=True)

class Listing_Actors(db.Model):
    __tablename__ = 'listing_Actors'

    listing_id = db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id'), nullable=False, primary_key=True)
    person_id = db.Column('person_id', db.String(16), db.ForeignKey('person.person_id'), nullable=False, primary_key=True)

class Genre(db.Model):
    __tablename__ = 'genre'

    genre_id = db.Column('genre_id', db.Integer, nullable=False, autoincrement=True, primary_key=True)
    genre = db.Column('genre', db.String(16), nullable=False)

class Listing_Genres(db.Model):
    __tablename__ = 'listing_genres'

    listing_id = db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id'), nullable=False, primary_key=True)
    genre_id = db.Column('genre_id', db.String(16), db.ForeignKey('genre.genre_id'), nullable=False, primary_key=True)

class Schedule(db.Model):
    __tablename__ = 'schedule'

    schedule_id = db.Column('schedule_id', db.Integer, nullable=False, autoincrement=True, primary_key=True)
    listing_id = db.Column('listing_id', db.String(16), db.ForeignKey('listing.listing_id'))
    title = db.Column('title', db.String(128))
    season = db.Column('season', db.Integer)
    episode = db.Column('episode', db.Integer)
    date = db.Column('datetime', db.DateTime)

class User(db.Model, flask_login.UserMixin):
    __tablename__ = 'users'

    username = db.Column('username', db.String(32), nullable=False, primary_key=True)
    password = db.Column('password', db.String(128), nullable=False)

    @property
    def id(self):
        return self.username

    def get_id(self):
        return self.username

class User_Subscriptions(db.Model):
    __tablename__ = 'user_subscriptions'

    user_id = db.Column('username', db.String(32), db.ForeignKey('users.username'), primary_key=True)
    listing_id = db.Column('listing_id', db.String(16), db.ForeignKey('listing.listing_id'), primary_key=True)
