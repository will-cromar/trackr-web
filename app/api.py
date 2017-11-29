"""Contains functionality for public REST API of web application."""
from app import app, models, cache, db
from .utils import passwordHash
from .notifications import batch_notifications
from flask import request
from flask.json import jsonify
from flask_jwt import JWT, jwt_required, current_identity
import json
from datetime import datetime, timedelta


def authenticate(username, password):
    """Authenticates credentials (HTTP) POSTed to /auth"""
    user = models.User.query.filter_by(username=username).first()
    if user and passwordHash(password) == user.password:
        return user


def identity(payload):
    """Get user object from JWT payload"""
    return models.User.query.filter_by(username=payload["identity"]).first()


# Initializes global state for session manager
jwt = JWT(app, authenticate, identity)


@app.route('/api/whoami')
@jwt_required()
def protected():
    """Tells user their username based on their JWT token"""
    return jsonify({"username": current_identity.username})


@app.route('/api/notifications')
@jwt_required()
def notifications():
    """Fetches notifications in cache for uesr based on JWT token"""

    key = current_identity.username
    return jsonify({'notifications': list(map(json.loads, cache.lrange(key, 0,
                                                                       -1)))})


@app.route('/api/createaccount', methods=['POST'])
def createaccount():
    """Creates user account from given username and password"""
    data = request.get_json()

    u = models.User(username=data['username'],
                    password=passwordHash(data['password']))
    db.session.add(u)
    db.session.commit()
    return jsonify({'status_code': "200"})


@app.route('/api/query')
def query():
    """Searches for the string in all fields of all listings and
    returns matches."""
    q = request.args.get('query')
    if q is None:
        listings = models.Listing.query.all()
    else:
        listings = models.Listing.query.filter(
            (models.Listing.title == q) |
            (models.Listing.description == q)).all()

        qgenre = models.Genre.query.filter_by(genre=q).first()
        if qgenre:
            listings.extend(qgenre.members)

        qperson = models.Person.query.filter_by(name=q).first()
        if qperson:
            listings.extend(qperson.directed)
            listings.extend(qperson.wrote)
            listings.extend(qperson.acted)

    res = list(map(models.Listing.todict, listings))
    return jsonify({'results': res})


@app.route('/api/getlisting')
def getlisting():
    """Get a listing by ID."""
    q = request.args.get('listing_id')

    if not q:
        return jsonify({})

    return jsonify(models.Listing.query.get(q).todict())


@app.route('/api/addsubscription', methods=['POST'])
@jwt_required()
def addsubscription():
    """Subscribe the current user to the given listing."""
    listing_id = request.get_json()['listing_id']
    username = current_identity.username

    u = models.User.query.get(username)
    l = models.Listing.query.get(listing_id)
    u.subscriptions.append(l)

    db.session.add(u)
    db.session.commit()

    return jsonify({'status_code': '200'})


@app.route('/api/subscriptions')
@jwt_required()
def subscriptions():
    """Gets all of the user's current subscriptions."""
    subs = current_identity.subscriptions
    res = list(map(models.Listing.todict, subs))
    return jsonify({'subscriptions': res})


@app.route('/api/genrelist')
def genreslist():
    """List all of the genres in the database."""
    res = list(map(models.Genre.todict, models.Genre.query.all()))
    return jsonify({'genres': res})


@app.route('/api/cachedump')
def cachedump():
    """Print all items in the cache."""
    return jsonify({key: list(map(json.loads, cache.lrange(key, 0, -1)))
                    for key in cache.keys()})


@app.route('/api/refreshcache')
def refreshcache():
    """Update the cache."""
    cache.flushall()
    batch_notifications()

    return "done"


# Utility endpoints


@app.route('/util/niccage')
def niccage():
    """Adds sample Nicolas Cage movies and subscribes admin."""
    nc = models.Person(name='Nicolas Cage')
    ba = models.Genre(genre_id=1337, genre='Bad action')

    l1 = models.Listing(title='Oviedo: The City of Chickens',
                        description='One last job.',
                        release_date=datetime.utcnow() + timedelta(days=2),
                        writers=[nc],
                        directors=[nc],
                        actors=[nc],
                        genres=[ba],
                        subscribers=[models.User.query.get('admin')])
    l2 = models.Listing(title='Biology: Chemistry in Disguise',
                        description='One last job.',
                        release_date=datetime.utcnow() + timedelta(days=4),
                        writers=[nc],
                        directors=[nc],
                        actors=[nc],
                        genres=[ba],
                        subscribers=[models.User.query.get('admin')])

    db.session.add(l1)
    db.session.add(l2)
    db.session.commit()

    return "done"


@app.route('/util/equifax')
def equifax():
    """Creates super secure admin account."""
    u = models.User(username='admin',
                    password=passwordHash('admin'),
                    is_admin=True)
    db.session.add(u)
    db.session.commit()
    return "done :)"
