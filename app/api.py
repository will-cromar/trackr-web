from app import app, models, cache, db
from .utils import passwordHash, generate_random_listings, model_dict
from flask import request
from flask.json import jsonify
from flask_jwt import JWT, jwt_required, current_identity

import json
import time
from datetime import datetime


def authenticate(username, password):
    """Authenticates credentials (HTTP) POSTed to /auth"""
    user = models.User.query.filter_by(username=username).first()
    if user and passwordHash(password) == user.password:
        return user


def identity(payload):
    """Get user object from JWT payload"""
    return models.User.query.filter_by(username=payload["identity"]).first()


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
    notifications_string = cache.get(current_identity.username)
    notifications = json.loads(notifications_string)

    return jsonify({'notifications': notifications})


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
    q = request.args.get('query')

    # TODO: Actually filter these
    listings = models.Listing.query.all()

    res = list(map(models.Listing.todict, listings))
    return jsonify({'results': res})


@app.route('/datadump')
def queryall():
    """Prints all movie names and release dates in database"""
    movies = models.Movie.query.all()
    moviesJson = [{"name": m.name, "releaseDate": m.releaseDate.timestamp()}
                  for m in movies]

    return jsonify(moviesJson)


@app.route('/api/addsubscription', methods=['POST'])
@jwt_required()
def addsubscription():
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
    subs = current_identity.subscriptions
    res = list(map(models.Listing.todict, subs))
    return jsonify({'subscriptions': res})


@app.route('/api/genrelist')
def genreslist():
    res = list(map(models.Genre.todict, models.Genre.query.all()))
    return jsonify({'genres': res})


@app.route('/api/cachedump')
def cachedump():
    return jsonify({key: cache[key] for key in cache.keys()})


@app.route('/api/refreshcache')
def refreshcache():
    userids = map(models.User.get_id, models.User.query.all())

    for u in userids:
        # TODO: Actually look up subscriptions
        notification = {'listing_id': 0,
                        'message': 'You have a notification!',
                        'time': int(time.time())}

        cache.set(u, json.dumps([notification]))

    return 'done'

# Utility endpoints


@app.route('/util/niccage')
def niccage():
    nc = models.Person(name='Nicolas Cage')
    ba = models.Genre(genre='Bad action')

    l1 = models.Listing(title='Oviedo: The City of Chickens',
                        description='One last job.',
                        release_date=datetime.utcnow(),
                        writers=[nc],
                        directors=[nc],
                        actors=[nc],
                        genres=[ba])
    l2 = models.Listing(title='Biology: Chemistry in Disguise',
                        description='One last job.',
                        release_date=datetime.utcnow(),
                        writers=[nc],
                        directors=[nc],
                        actors=[nc],
                        genres=[ba])

    db.session.add(l1)
    db.session.add(l2)
    db.session.commit()

    return "done"


@app.route('/util/equifax')
def equifax():
    u = models.User(username='admin',
                    password=passwordHash('admin'),
                    is_admin=True)
    db.session.add(u)
    db.session.commit()
    return "done :)"