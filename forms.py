from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FieldList, FormField, DateField
from wtforms.validators import DataRequired

# class PostForm(FlaskForm):
#     title = StringField('title', validators=[DataRequired()])
#     description  = TextAreaField('description')
#     release_date = DateField('release_date(d/m/Y)', format = '%m/%d/%Y', validators=[DataRequired()])
#     # time = IntegerField('time', validators=[DataRequired()])
#     directors = StringField('directors')
#     actors = StringField('actors')
#     writers = StringField('writers')
#     genres = StringField('genre')
#     date = DateField('date(m/d/Y)', format = '%m/%d/%Y')
#     season = IntegerField('season')
#     episode = IntegerField('episode')
#     # episode_title = StringField()

class MovieForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    genres = StringField('genres', validators=[DataRequired()])
    description  = TextAreaField('description')
    release_date = DateField('release_date(m/d/Y)', format = '%m/%d/%Y', validators=[DataRequired()])
    writers = StringField('writers')
    directors = StringField('directors')
    actors = StringField('actors')

class ShowForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    description  = TextAreaField('description')
    genre = StringField('genre', validators=[DataRequired()])
    season = IntegerField('season')
    episode = IntegerField('episode')
    episode_title = StringField('episode_title')
    date = DateField('date(m/d/Y)',format='%m/%d/%Y')
    writers = StringField('writers')
    directors = StringField('directors')
    actors = StringField('actors')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


SignupForm = LoginForm
