from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash

from models import MyDB


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Неверный логин'),
                                                Length(min=2, max=15, message='Неверная длина логина')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Неверный пароль'),
                                                   Length(min=2, max=25, message='Неверная длина пароля')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')

    def validate_username(self, username):
        user = username.data
        db_conn = MyDB()
        records = db_conn.query('SELECT username FROM uuser WHERE username = %s', (user,))
        if not records:
            raise ValidationError('Такого пользователя не существует')

    def validate_password(self, password):
        pas = password.data
        user = self.username.data
        db_conn = MyDB()
        records = db_conn.query('SELECT ppassword FROM uuser WHERE username = %s', (user,))
        if records:
            if not check_password_hash(records[0][0], pas):
                raise ValidationError('Неверный пароль')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Обязательное поле'),
                                                Length(min=2, max=15, message='Неверная длина логина')])
    email = StringField('Email', validators=[DataRequired(message='Обязательное поле'),
                                             Email(message='Проверьте правильность ввода адреса')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Обязательное поле'),
                                                   Length(min=2, max=25, message='Неверная длина пароля')])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(message='Обязательное поле'),
                                        Length(min=2, max=25, message='Неверная длина пароля'),
                                        EqualTo('password', message='Пароли должны совпадать')])
    age = DateField('Дата рождения', format='%Y-%m-%d')
    level = RadioField('Уровень подготовки', choices=[('Новичок', 'Новичок'), ('Средний', 'Средний'),
                                                      ('Профи', 'Профи')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = username.data
        db_conn = MyDB()
        records = db_conn.query('SELECT username FROM uuser WHERE username = %s', (user,))
        if records:
            raise ValidationError('Данный Логин уже занят')

    def validate_email(self, email):
        mail = email.data
        db_conn = MyDB()
        records = db_conn.query('SELECT email FROM uuser WHERE email = %s', (mail,))
        if records:
            raise ValidationError('Данная почта уже зарегистрирована')
