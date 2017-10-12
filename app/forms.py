from flask_wtf import Form
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class PostForm(Form):
    title = StringField('title', validators=[DataRequired()])
    time = IntegerField('time', validators=[DataRequired()])


class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


SignupForm = LoginForm
