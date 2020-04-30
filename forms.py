from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Неверный логин'),
                                                Length(min=2, max=15, message='Неверная длина логина')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Неверный пароль'),
                                                   Length(min=2, max=25, message='Неверная длина пароля')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Вход')


class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(message='Обязательное поле'),
                                             Length(min=2, max=15, message='Неверная длина логина')])
    email = StringField('Email', validators=[DataRequired(message='Обязательное поле'),
                                             Email(message='Проверьте правильность ввода адреса')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Обязательное поле'),
                                                   Length(min=2, max=25, message='Неверная длина пароля')])
    age = DateField('Дата рождения', format='%Y-%m-%d')
    level = RadioField('Уровень подготовки', choices=[('Новичок', 'Новичок'), ('Средний', 'Средний'),
                                                      ('Профи', 'Профи')])
    submit = SubmitField('Зарегистрироваться')
