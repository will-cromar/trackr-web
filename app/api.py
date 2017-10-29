from app import app, models, cache
from .utils import passwordHash, generate_random_listings
from flask.json import jsonify
from flask_jwt import JWT, jwt_required, current_identity

import json
import time


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
    notification_string = cache.get(current_identity.username)
    notification = json.loads(notification_string)

    return jsonify(notification)


@app.route('/datadump')
def queryall():
    """Prints all movie names and release dates in database"""
    movies = models.Movie.query.all()
    moviesJson = [{"name": m.name, "releaseDate": m.releaseDate.timestamp()}
                  for m in movies]

    return jsonify(moviesJson)


@app.route('/api/subscriptions')
# TODO: Implement this for real and enable jwt auth
def subscriptions():
    return jsonify({'subscriptions': generate_random_listings()})


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

        cache.set(u, json.dumps(notification))

    return 'done'