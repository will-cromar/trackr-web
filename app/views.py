from flask import render_template, flash, redirect, request
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, models, login_manager
from .utils import passwordHash
from .forms import MovieForm, EpisodeForm, LoginForm, SignupForm
from .notifications import notify_neighbors
import datetime

@login_manager.user_loader
def load_user(user_id):
    u = models.User.query.get(user_id)
    return u


@app.route('/')
def index():
    """Home page"""
    return render_template('base.html')


@app.route('/addlisting')
@login_required
def addmovie():
    """Form to add new movies to the database"""
    form = MovieForm()
    return render_template('addlisting.html',
                           title='Add Listing',
                           form=form)


@app.route('/addlisting/submit', methods=['POST'])
@login_required
def postmovie():
    """Submit Movie entry form"""
    form = MovieForm()
    if not current_user.is_admin:
        flash("You must be an admin to make changes to the database.")
    elif form.validate_on_submit():
        if form.update_id.data:
            m = models.Listing.query.get(form.update_id.data)
            if m is None:
                flash("Update ID is invalid.")
                return redirect('/addlisting')
        else:
            m = models.Listing()

        director_strings = form.directors.data.split(",")
        directors = list(map(models.Person.make_or_get, director_strings))
        writer_strings = form.writers.data.split(",")
        writers = list(map(models.Person.make_or_get, writer_strings))
        actor_strings = form.actors.data.split(",")
        actors = list(map(models.Person.make_or_get, actor_strings))
        genre_strings = form.genres.data.split(",")
        genres = list(map(models.Genre.make_or_get, genre_strings))

        m.title = form.title.data
        m.description = form.description.data
        m.release_date = form.release_date.data
        m.directors = directors
        m.writers = writers
        m.actors = actors
        m.genres = genres

        db.session.add(m)
        db.session.commit()
        flash("Submitted entry as ID {}".format(m.listing_id))
        notify_neighbors(models.Listing.query.all(), models.Listing.query.get(m.listing_id))
    else:
        for fieldName, errorMessage in form.errors.items():
            flash("ERROR: {} {}".format(fieldName, errorMessage))

    return redirect('/addlisting')


@app.route('/addepisode')
@login_required
def addepisode():
    form = EpisodeForm()
    return render_template('addepisode.html',
                           title='Add Episode',
                           form=form)


@app.route('/addepisode/submit', methods=['POST'])
@login_required
def submitepisode():
    form = EpisodeForm()

    if not current_user.is_admin:
        flash("You must be an admin to make changes to the database.")
    elif form.validate_on_submit():
        listing = models.Listing.query.filter_by(
            listing_id=form.listing_id.data).first()
        if not listing:
            flash("Listing ID is not valid")
            return redirect('/addepisode')

        date = form.date.data
        delta = datetime.timedelta(hours=form.hour.data,
                                   minutes=form.minute.data)
        dt = date + delta

        s = models.Schedule(
            listing_id=form.listing_id.data,
            title=form.title.data,
            season=form.season.data,
            episode=form.episode.data,
            date=dt
        )
        db.session.add(s)
        db.session.commit()
        flash("Added episode ID {} successfully".format(s.schedule_id))
    else:
        for fieldName, errorMessage in form.errors.items():
            flash("ERROR: {} {}".format(fieldName, errorMessage))

    return redirect('/addepisode')


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

@app.route('/manageusers')
@login_required
def manageusers():
    """Allows admin users to promote other users"""
    return render_template('manageusers.html',
                           users=models.User.query.all())


@app.route('/promote')
@login_required
def promote():
    if not current_user.is_admin:
        flash("You must be an admin to do this.")
        return redirect('/login')

    username = request.args.get('user')
    u = models.User.query.get(username)
    u.is_admin = True
    db.session.add(u)
    db.session.commit()

    flash("{} has been promoted".format(username))
    return redirect('/manageusers')


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


@app.route('/init')
def create_db():
    """Creates new database tables based on definitions in models.py"""
    db.create_all()

    return redirect('/')
