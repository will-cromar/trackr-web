"""Contains database models used by web application."""
from datetime import datetime
from app import db
import flask_login

listing_writers = db.Table(
    'listing_writers', db.Model.metadata,
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.person_id'))
)

listing_directors = db.Table(
    'listing_directors', db.Model.metadata,
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.person_id'))
)

listing_actors = db.Table(
    'listing_actors', db.Model.metadata,
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.person_id'))
)

listing_genres = db.Table(
    'listing_genres', db.Model.metadata,
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.genre_id'))
)

user_subscriptions = db.Table(
    'user_subscriptions', db.Model.metadata,
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.listing_id')),
    db.Column('user_id', db.String(32), db.ForeignKey('user.username'))
)


class Listing(db.Model):
    __tablename__ = 'listing'

    listing_id = db.Column('listing_id', db.Integer, nullable=False,
                           autoincrement=True, primary_key=True)
    title = db.Column('title', db.String(128), nullable=False)
    description = db.Column('description', db.String(4096))
    release_date = db.Column('release_date', db.DateTime)
    directors = db.relationship('Person',
                                back_populates='directed',
                                secondary=listing_directors)
    writers = db.relationship('Person',
                              back_populates='wrote',
                              secondary=listing_writers)
    actors = db.relationship('Person',
                             back_populates='acted',
                             secondary=listing_actors)
    genres = db.relationship('Genre',
                             back_populates='members',
                             secondary=listing_genres)
    subscribers = db.relationship('User',
                                  back_populates='subscriptions',
                                  secondary=user_subscriptions)

    def todict(self):
        res = {
            'listing_id': self.listing_id,
            'title': self.title,
            'description': self.description,
            'release_date': int(self.release_date.timestamp()),
            'directors': list(map(Person.todict, self.directors)),
            'writers': list(map(Person.todict, self.writers)),
            'actors': list(map(Person.todict, self.actors)),
            'genres': list(map(Genre.todict, self.genres)),
        }

        schedules = Schedule.query.filter(Schedule.listing_id == self.listing_id).all()
        if len(schedules) > 0:
            res['schedules'] = list(map(Schedule.todict, schedules))

        return res

    @property
    def delta(self):
        return self.time - datetime.utcnow()


class Person(db.Model):
    __tablename__ = 'person'

    person_id = db.Column('person_id', db.Integer, nullable=False,
                          autoincrement=True, primary_key=True)
    name = db.Column('name', db.String(128), nullable=False)
    directed = db.relationship(
        'Listing',
        back_populates='directors',
        secondary=listing_directors)
    wrote = db.relationship(
        'Listing',
        back_populates='writers',
        secondary=listing_writers)
    acted = db.relationship(
        'Listing',
        back_populates='actors',
        secondary=listing_actors)

    def todict(self):
        return {
            'person_id': self.person_id,
            'name': self.name
        }

    def make_or_get(name):
        """If an entry exists with name, return it. Otherwise, make a new one."""
        q = Person.query.filter(Person.name == name).all()
        return q[0] if len(q) > 0 else Person(name=name)


class Genre(db.Model):
    __tablename__ = 'genre'

    genre_id = db.Column('genre_id', db.Integer, nullable=False,
                         autoincrement=True, primary_key=True)
    genre = db.Column('genre', db.String(16), nullable=False)
    members = db.relationship(
        'Listing',
        back_populates='genres',
        secondary=listing_genres)

    def todict(self):
        return {
            'genre_id': self.genre_id,
            'genre': self.genre
        }

    def make_or_get(name):
        """If an entry exists with name, return it. Otherwise, make a new one."""
        q = Genre.query.filter(Genre.genre == name).all()
        return q[0] if len(q) > 0 else Genre(genre=name)


class Schedule(db.Model):
    __tablename__ = 'schedule'

    schedule_id = db.Column('schedule_id', db.Integer, nullable=False,
                            autoincrement=True, primary_key=True)
    listing_id = db.Column('listing_id', db.Integer,
                           db.ForeignKey('listing.listing_id'))
    title = db.Column('title', db.String(128))
    season = db.Column('season', db.Integer)
    episode = db.Column('episode', db.Integer)
    date = db.Column('datetime', db.DateTime)

    def todict(self):
        return {
            'schedule_id': self.schedule_id,
            'listing_id': self.listing_id,
            'title': self.title,
            'season': self.season,
            'episode': self.episode,
            'date': int(self.date.timestamp()),
        }


class User(db.Model, flask_login.UserMixin):
    __tablename__ = 'user'

    username = db.Column('username', db.String(32), nullable=False,
                         primary_key=True)
    password = db.Column('password', db.String(128), nullable=False)
    is_admin = db.Column('is_admin', db.Boolean, default=False)
    subscriptions = db.relationship('Listing',
                                    back_populates='subscribers',
                                    secondary=user_subscriptions)

    @property
    def id(self):
        return self.username

    def get_id(self):
        return self.username
