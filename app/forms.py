from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    time = IntegerField('time', validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


SignupForm = LoginForm
