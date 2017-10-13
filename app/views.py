from flask import render_template, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from app import app, db, models, login_manager
from .utils import passwordHash
from .forms import PostForm, LoginForm, SignupForm


@login_manager.user_loader
def load_user(user_id):
    u = models.User.query.get(user_id)
    return u


@app.route('/')
def index():
    """Home page"""
    return render_template('base.html')


@app.route('/addmedia')
@app.route('/admin')
@login_required
def addmedia():
    """Form to add new content to the database"""
    form = PostForm()

    movies = models.Movie.query.all()
    return render_template('addmedia.html',
                           title='Home',
                           movies=movies,
                           form=form)


@app.route('/postmedia', methods=['POST'])
@login_required
def postmedia():
    """Submit content entry form"""
    form = PostForm()
    if form.validate_on_submit():
        m = models.Movie(title=form.title.data,
                         time=datetime.fromtimestamp(form.time.data),
                         author=current_user.username)
        db.session.add(m)
        db.session.commit()
        flash("Submitted entry for ID {}".format(m.media_id))
    else:
        for fieldName, errorMessage in form.errors.items():
            flash("ERROR: {} {}".format(fieldName, errorMessage))

    return redirect('/addmedia')


@app.route('/signup')
def signup():
    """Form to create user account"""
    form = SignupForm()
    return render_template('signup.html',
                           form=form)


@app.route('/createuser', methods=['POST'])
def createuser():
    """Submit signup form"""
    form = SignupForm()
    if form.validate_on_submit():
        u = models.User(username=form.username.data,
                        password=passwordHash(form.password.data))
        db.session.add(u)
        db.session.commit()
        login_user(u)
        flash('Created user "{}"'.format(u.username))
    else:
        for fieldName, errorMessage in form.errors.items():
            flash("ERROR: {} {}".format(fieldName, errorMessage))

    return redirect('/')


@app.route('/login')
def login():
    """Form to log into user account"""
    form = LoginForm()

    return render_template('login.html',
                           form=form)


@app.route('/checkcredentials', methods=['POST'])
def checkcredentials():
    """Submit login form"""
    form = LoginForm()
    if form.validate_on_submit():
        u = models.User.query.get(form.username.data)
        if u.password == passwordHash(form.password.data):
            flash('Logged in as "{}"'.format(u.username))
            login_user(u)
        else:
            flash('Do better.')
            return redirect('/login')
    else:
        flash('Error submitting form')
        return redirect('/login')

    return redirect('/')


@app.route('/whoami')
@login_required
def whoami():
    """Returns current user's username"""
    return current_user.username


@app.route('/logout')
@login_required
def logout():
    """Logs user out"""
    logout_user()
    return redirect('/login')


@app.route('/datadump')
def queryall():
    movies = models.Movie.query.all()

    # HACK: get movie data in a JSON format compatible with the test app.
    # There is almost certainly a better way to do this.
    moviesJson = ["{{\"name\": \"{}\", \"releaseDate\": {}}}".format(
        movie.title, movie.time.timestamp()) for movie in movies]
    return "[{}]".format(", ".join(moviesJson))


@app.route('/hcf')
def reset_db():
    """Deletes and re-creates DB"""
    os.remove('app.db')
    db.create_all()

    return redirect('/')


@app.route('/init')
def create_db():
    db.create_all()

    return redirect('/')