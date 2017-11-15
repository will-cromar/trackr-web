from flask import render_template, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
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


# @app.route('/addmedia')
# @app.route('/admin')
# @login_required
# def addmedia():
#     """Form to add new content to the database"""
#     form = PostForm()
#
#     movies = models.Movie.query.all()
#     return render_template('addmedia.html',
#                            title='Home',
#                            movies=movies,
#                            form=form)


# @app.route('/postmedia', methods=['POST'])
# @login_required
# def postmedia():
#     """Submit content entry form"""
#     form = PostForm()
#     if form.validate_on_submit():
#         m = models.Movie(name=form.title.data,
#                          releaseDate=datetime.fromtimestamp(form.time.data),
#                          author=current_user.username)
#         db.session.add(m)
#         db.session.commit()
#         flash("Submitted entry for ID {}".format(m.media_id))
#     else:
#         for fieldName, errorMessage in form.errors.items():
#             flash("ERROR: {} {}".format(fieldName, errorMessage))
#
#     return redirect('/addmedia')



@app.route('/addmovie')
# @app.route('/admin')
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
    if form.validate_on_submit():
        m = models.Listing( title =form.title.data,
                         release_date = form.release_date(),
                         genres = form.genres(),
                         writers = form.writers(),
                         directors = form.directors(),
                         actors = form.actors(),
                         description = form.description()
                         )
        db.session.add(m)
        db.session.commit()
        flash("Submitted entry for ID {}".format(m.title.data))
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



@app.route('/postshow', methods=['POST'])
@login_required
def postshow():
    """Submit show content entry form"""
    form = ShowForm()
    if form.validate_on_submit():
        s = models.Listing( title =form.title.data,
                         season = form.season(),
                         episode = form.episode(),
                         episode_title = form.episode_title(),
                         date = form.date(),
                         genre = form.genre(),
                         writers = form.writers(),
                         directors = form.directors(),
                         actors = form.actors(),
                         description = form.description())
        db.session.add(s)
        db.session.commit()
        flash("Submitted entry for ID {}".format(s.listing_id))
    else:
        for fieldName, errorMessage in form.errors.items():
            flash("ERROR: {} {}".format(fieldName, errorMessage))

    return redirect('/addshow')














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
