from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Optional


class MovieForm(FlaskForm):
    update_id = IntegerField('update_id', validators=[Optional()])
    title = StringField('title', validators=[InputRequired()])
    genres = StringField('genres', validators=[InputRequired()])
    description = TextAreaField('description', validators=[InputRequired()])
    release_date = DateField('release_date', validators=[InputRequired()])
    writers = StringField('writers', validators=[InputRequired()])
    directors = StringField('directors', validators=[InputRequired()])
    actors = StringField('actors', validators=[InputRequired()])


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
    password = PasswordField('password', validators=[DataRequired()])


SignupForm = LoginForm
