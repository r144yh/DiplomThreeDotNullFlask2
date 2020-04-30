from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(),
                                                Length(min=2, max=15, message='Неверный логин')])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   Length(min=2, max=25, message='Неверная длина пароля')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
