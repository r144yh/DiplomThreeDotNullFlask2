from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from config import Config
from forms import LoginForm, RegistrationForm, EditProfileForm, Exercise, ExercisePage, Training, CreateTraining
from models import User, MyDB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_material import Material
from datetime import date, datetime, timedelta
import json

app = Flask('__main__',
            template_folder='frontend/templates',
            static_folder='frontend/static')
material = Material(app)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
def main():
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('profile', user_id=current_user.id))


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile', user_id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        db_conn = MyDB()
        records = db_conn.query('SELECT user_id FROM uuser WHERE username = %s',
                                (form.username.data,))
        if not records:
            return redirect(url_for('login'))
        user = User(records[0][0])
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('profile', user_id=current_user.id)
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = generate_password_hash(form.password.data)
        db_conn = MyDB()
        form.level.data = int(form.level.data)
        db_conn.query('INSERT INTO uuser(user_id, username, email, ppassword, height, weight, age, gender, level, '
                      'levelBody, count_of_tran) '
                      'VALUES(DEFAULT, %s, %s, %s, DEFAULT, DEFAULT, %s, %s, %s, %s, DEFAULT)',
                      (form.username.data, form.email.data, hash_password, form.age.data, form.gender.data,
                       form.level.data, form.levelBody.data))
        db_conn.db_commit()
        return redirect(url_for('login'))
    return render_template('registration.html', title='Registration', form=form)


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if current_user.id != user_id:
        return redirect(url_for('info'))
    db_conn = MyDB()
    records = db_conn.query('SELECT username, email, height, weight, age, gender, level, levelBody,'
                            ' count_of_tran, date_of_reg '
                            'FROM uuser WHERE user_id = %s', (current_user.id,))
    rev = records[0][9].strftime("%d/%m/%Y")
    records2 = db_conn.query('SELECT user_exercise.ex_id, name_of_ex, count_of_workout, count_of_repeat, '
                             'count_of_last_ex, time_of_last_ex, date_of_ex, date_of_add '
                             'FROM user_exercise INNER JOIN exercise ON user_exercise.ex_id = exercise.ex_id  '
                             'WHERE user_id = %s', (current_user.id,))
    major = True
    if records2 == []:
        major = False
    # if records2[0][6] > now - 30:

    records3 = db_conn.query('SELECT user_tran.train_id, training.name_of_tran, count_of_workout, count_of_repeat, '
                             'time_of_last_ex '
                             'FROM user_tran NATURAL JOIN training '
                             'WHERE user_id = %s', (current_user.id,))
    major2 = True
    if records3 == []:
        major2 = False
    return render_template('profile.html', title='Profile', records=records, rev=rev, records2=records2, major=major,
                           records3=records3, major2=major2)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        db_conn = MyDB()
        db_conn.query(
            'UPDATE uuser SET username = %s, height = %s, weight = %s WHERE '
            'user_id = %s',
            (form.username.data, form.height.data, form.weight.data, current_user.id))
        db_conn.db_commit()
        return redirect(url_for('profile', user_id=current_user.id))
    elif request.method == 'GET':
        db_conn = MyDB()
        db_conn.query('SELECT username, height, weight '
                      'FROM uuser '
                      'WHERE user_id = %s',
                      (current_user.id,))
        form.username.data = current_user.username
        form.height.data = current_user.userHeight
        form.weight.data = current_user.userWeight
    return render_template('editProfile.html', title='Edit Profile', form=form)


@app.route("/exercises", methods=['GET', 'POST'])
def exercises():
    if current_user.is_anonymous:
        return redirect(url_for('info'))
    else:
        form = Exercise()
        now = date.today()
        db_conn = MyDB()
        records = db_conn.query('SELECT ex_id, name_of_ex, descr_of_ex, level_of_ex, type_of_ex, body_part, '
                                'number_of_points '
                                'FROM exercise '
                                'WHERE ex_id NOT IN (SELECT ex_id '
                                'FROM user_exercise '
                                'WHERE user_id = %s)',
                                current_user.id)
        if form.validate_on_submit():
            db_conn.query(
                'INSERT INTO user_exercise(user_ex_id, ex_id, user_id, time_of_last_ex, date_of_add) '
                'VALUES (DEFAULT, %s, %s, %s, %s)',
                (form.exId.data, current_user.id, '00:00:00', now))
            db_conn.db_commit()
            return redirect(url_for('profile', user_id=current_user.id))
    return render_template('exercises.html', title='Exercises', records=records, form=form)


@app.route('/exercises/<ex_id>', methods=['GET', 'POST'])
def ex_page(ex_id):
    if current_user.is_anonymous:
        return redirect(url_for('info'))
    else:
        form = ExercisePage()
        now = date.today()
        db_conn = MyDB()
        records = db_conn.query('SELECT * '
                                'FROM exercise NATURAL JOIN user_exercise '
                                'WHERE user_id = %s and ex_id = %s',
                                (current_user.id, ex_id))
        if form.validate_on_submit():
            timeEnd = datetime.strptime(form.timeOfEx.data, '%H:%M:%S').time()
            # timeStart = db_conn.query('SELECT time_of_last_ex '
            #                           'FROM user_exercise '
            #                           'WHERE user_id = %s and ex_id = %s',
            #                           (current_user.id, ex_id))
            # newTime = str(timeStart[0][0].hour + timeEnd.hour) + ':' + str(
            #     timeStart[0][0].minute + timeEnd.minute) + ':' + str(timeStart[0][0].second + timeEnd.second)
            db_conn.query(
                'UPDATE user_exercise SET count_of_repeat = count_of_repeat + %s, count_of_workout =  '
                'count_of_workout + 1, date_of_ex = %s, time_of_last_ex = %s '
                'WHERE ex_id = %s and user_id = %s ',
                (form.count.data, now, timeEnd, ex_id, current_user.id))
            db_conn.db_commit()
            level = db_conn.query(
                'UPDATE uuser SET count_of_tran = count_of_tran + 1, level = level + 20 '
                'WHERE user_id = %s RETURNING level',
                (current_user.id,))
            db_conn.db_commit()
            return redirect(url_for('profile', user_id=current_user.id))
        return render_template('ex_page.html', title='Profile', records=records, form=form)


@app.route("/training", methods=['GET', 'POST'])
def training():
    if current_user.is_anonymous:
        return redirect(url_for('info'))
    else:
        form = Exercise()
        db_conn = MyDB()
        records = db_conn.query('SELECT train_id, name_of_tran, complexity, descroftrain '
                                'FROM training '
                                'WHERE user_tran = FALSE and train_id NOT IN (SELECT train_id '
                                'FROM user_tran '
                                'WHERE user_id = %s)',
                                current_user.id)
        if form.validate_on_submit():
            db_conn.query(
                'INSERT INTO user_tran(user_tran_id, train_id, user_id, time_of_last_ex) '
                'VALUES (DEFAULT, %s, %s, %s)',
                (form.exId.data, current_user.id, '00:00:00'))
            db_conn.db_commit()
            return redirect(url_for('profile', user_id=current_user.id))
    return render_template('training.html', title='Training', form=form, records=records)


@app.route("/createTraining", methods=['GET', 'POST'])
def createTraining():
    if current_user.is_anonymous:
        return redirect(url_for('info'))
    else:
        db_conn = MyDB()
        choices = db_conn.query('SELECT ex_id, name_of_ex FROM exercise')

        form = CreateTraining()
        form.typeOfEx.choices = choices
        form.typeOfEx2.choices = choices
        form.typeOfEx3.choices = choices
        form.typeOfEx4.choices = choices
        if form.validate_on_submit():
            ansList = [form.typeOfEx.data, form.typeOfEx2.data, form.typeOfEx3.data, ]
            tranId = db_conn.query('INSERT INTO training(train_id, name_of_tran, user_tran, complexity) VALUES ('
                                   'DEFAULT, %s, '
                                   'True, %s) RETURNING train_id', (form.nameOfTran.data, form.complexity.data))
            db_conn.db_commit()
            for ans in ansList:
                db_conn.query('INSERT INTO exercise_tran(ex_id, train_id) VALUES(%s, %s)', (ans, tranId[0]))
                db_conn.db_commit()
            db_conn.query('INSERT INTO user_tran(user_tran_id, user_id, train_id, time_of_last_ex) VALUES(DEFAULT, '
                          '%s, %s, %s)',
                          (current_user.id, tranId[0], '00:00:00'))
            db_conn.db_commit()
            return redirect(url_for('profile', user_id=current_user.id))
        return render_template('createTran.html', title='Create Training', form=form)


@app.route('/training/<tran_id>', methods=['GET', 'POST'])
def training_page(tran_id):
    if current_user.is_anonymous:
        return redirect(url_for('info'))
    else:
        form = ExercisePage()
        now = date.today()
        db_conn = MyDB()
        records = db_conn.query('SELECT name_of_tran, complexity '
                                'FROM user_tran NATURAL JOIN training '
                                'WHERE user_id = %s and train_id = %s',
                                (current_user.id, tran_id))
        records2 = db_conn.query('SELECT * '
                                 'FROM user_tran NATURAL JOIN exercise_tran NATURAL JOIN exercise '
                                 'WHERE user_id = %s and train_id = %s',
                                 (current_user.id, tran_id))
        if form.validate_on_submit():
            timeEnd = datetime.strptime(form.timeOfEx.data, '%H:%M:%S').time()
            db_conn.query(
                'UPDATE user_tran SET count_of_repeat = count_of_repeat + %s, count_of_workout =  '
                'count_of_workout + 1, date_of_train = %s, time_of_last_ex = %s '
                'WHERE train_id = %s and user_id = %s ',
                (form.count.data, now, timeEnd, tran_id, current_user.id))
            db_conn.db_commit()
            db_conn.query(
                'UPDATE uuser SET count_of_tran = count_of_tran + 1, level = level + 50 '
                'WHERE user_id = %s ',
                (current_user.id,))
            db_conn.db_commit()
            return redirect(url_for('profile', user_id=current_user.id))
        return render_template('training_page.html', title='Profile', records=records, form=form, records2=records2)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
