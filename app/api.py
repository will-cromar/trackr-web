from app import app, models, cache, db
from .utils import passwordHash, generate_random_listings, model_dict
from .notifications import get_notifications
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

    if current_identity.username not in cache.keys():
        notifications = get_notifications()
        for notif in notifications:
            print(notifications[notif])
            cache.set(notif, json.dumps(notifications[notif]))
    else:
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
    q = request.args.get('listing_id')

    if not q:
        return jsonify({})

    return jsonify(models.Listing.query.get(q).todict())


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

    notifications = get_notifications()
    for u in userids:
        cache.set(u, json.dumps(notifications[u]))

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
