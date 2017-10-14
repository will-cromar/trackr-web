from app import app, models
from .utils import passwordHash
from flask.json import jsonify
from flask_jwt import JWT, jwt_required, current_identity


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


@app.route('/datadump')
def queryall():
    """Prints all movie names and release dates in database"""
    movies = models.Movie.query.all()
    moviesJson = [{"name": m.name, "releaseDate": m.releaseDate.timestamp()}
                  for m in movies]

    return jsonify(moviesJson)
