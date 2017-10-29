import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Get database URI from environment variables, or default to SQLite if
# not available
SQLITE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', SQLITE_URI)
SQLALCHEMY_TRACK_MODIFICATIONS = False

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
