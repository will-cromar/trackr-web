from flask import render_template, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, models, login_manager
from .utils import passwordHash
from .forms import MovieForm, ShowForm, LoginForm, SignupForm

@login_manager.user_loader
def load_user(user_id):
    u = models.User.query.get(user_id)
    return u


@app.route('/')
def index():
    """Home page"""
    return render_template('base.html')


@app.route('/addmovie')
@login_required
def addmovie():
    """Form to add new movies to the database"""
    form = MovieForm()
    # movies = models.Movie.query.all()
    return render_template('addmovie.html',
                           title='Home',
                           form=form)


@app.route('/postmovie', methods=['POST'])
@login_required
def postmovie():
    """Submit Movie entry form"""
    form = MovieForm()
    if not current_user.is_admin:
        flash("You must be an admin to make changes to the database.")
    elif form.validate_on_submit():
        director_strings = form.directors.data.split(",")
        directors = list(map(models.Person.make_or_get, director_strings))
        writer_strings = form.writers.data.split(",")
        writers = list(map(models.Person.make_or_get, writer_strings))
        actor_strings = form.actors.data.split(",")
        actors = list(map(models.Person.make_or_get, actor_strings))
        genre_strings = form.genres.data.split(",")
        genres = list(map(models.Genre.make_or_get, genre_strings))
        m = models.Listing(title=form.title.data,
                           description=form.description.data,
                           release_date=form.release_date.data,
                           directors=directors,
                           writers=writers,
                           actors=actors,
                           genres=genres)
        db.session.add(m)
        db.session.commit()
        flash("Submitted entry for ID {}".format(m.title))
    else:
        for fieldName, errorMessage in form.errors.items():
            flash("ERROR: {} {}".format(fieldName, errorMessage))

    return redirect('/addmovie')


@app.route('/addshow')
@login_required
def addshow():
    """Form to add new shows to the database"""
    form = ShowForm()
    return render_template('addshow.html',
                           title='Home',
                           form=form)


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


@app.route('/init')
def create_db():
    """Creates new database tables based on definitions in models.py"""
    db.create_all()

    return redirect('/')
