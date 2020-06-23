from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, DecimalField, SelectField, \
    SelectMultipleField
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
    gender = SelectField('Пол', choices=[('Женский', 'Женский'), ('Мужской', 'Мужской')])
    level = SelectField('Уровень физической подготовки', choices=[('0', 'Новичок'), ('700', 'Средний'),
                                                                  ('1000', 'Профи')])
    levelBody = SelectField('Ваша физическая форма', choices=[('Недостаточный вес', 'Имею недостаточный вес'),
                                                              ('В пределах нормы', 'Форма в пределах нормы'),
                                                              ('Избыточный вес', 'Имею избыточный вес')])
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


class EditProfileForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=2, max=15, message='Неверная длина логина')])
    height = DecimalField('Рост', validators=[NumberRange(min=0, max=300)])
    weight = DecimalField('Текущий вес', validators=[NumberRange(min=20, max=300)])
    submit = SubmitField('Сохранить изменения')


class Exercise(FlaskForm):
    exId = DecimalField('Id')
    submit = SubmitField('Добавить к себе')


class ExercisePage(FlaskForm):
    count = DecimalField('Кол-во повторений', validators=[NumberRange(min=0, max=300)])
    submit = SubmitField('Подтвердить')


class Training(FlaskForm):
    count = DecimalField('Кол-во повторений', validators=[NumberRange(min=0, max=300)])
    exId = DecimalField('Id')
    submit = SubmitField('Добавить к себе')


class CreateTraining(FlaskForm):
    nameOfTran = StringField('Название программы')
    complexity = SelectField('Выбор упражнений', choices=[('hard', 'Тяжелая тренировка'),
                                                          ('medium', 'Средней сложности'),
                                                          ('easy', 'Легкая тренировка')])
    typeOfEx = SelectField('Выбор упражнений', coerce=int)
    typeOfEx2 = SelectField('Выбор упражнений', coerce=int)
    #typeOfEx3 = SelectField('Выбор упражнений', coerce=int)
    # typeOfEx4 = SelectField('Выбор упражнений', coerce=int)
    # typeOfEx5 = SelectField('Выбор упражнений', coerce=int)
    submit = SubmitField('Добавить к себе')
