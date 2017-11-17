from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, NumberRange


class MovieForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    genres = StringField('genres', validators=[DataRequired()])
    description = TextAreaField('description')
    release_date = DateField('release_date')
    writers = StringField('writers')
    directors = StringField('directors')
    actors = StringField('actors')


class EpisodeForm(FlaskForm):
    listing_id = IntegerField('listing_id', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    season = IntegerField('season', validators=[DataRequired()])
    episode = IntegerField('episode', validators=[DataRequired()])
    date = DateField('date', validators=[DataRequired()])
    hour = IntegerField('hour', validators=[InputRequired(), NumberRange(0, 23)])
    minute = IntegerField('minute', validators=[InputRequired(), NumberRange(0, 59)])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


SignupForm = LoginForm
