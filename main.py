from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from config import Config
from forms import LoginForm, RegistrationForm, EditProfileForm, Exercise
from models import User, MyDB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_material import Material

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
        return redirect(url_for('error_404'))
    db_conn = MyDB()
    records = db_conn.query('SELECT username, email, height, weight, age, gender, level, levelBody,'
                            ' count_of_tran, date_of_reg '
                            'FROM uuser WHERE user_id = %s', (current_user.id,))
    rev = records[0][9].strftime("%d/%m/%Y")
    return render_template('profile.html', title='Profile', records=records, rev=rev)


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
                      'FROM uuser  '
                      'WHERE user_id = %s',
                      (current_user.id,))
        form.username.data = current_user.username
        form.height.data = current_user.userHeight
        form.weight.data = current_user.userWeight
    return render_template('editProfile.html', title='Edit Profile', form=form)


@app.route("/exercises", methods=['GET', 'POST'])
@login_required
def exercises():
    form = Exercise()
    db_conn = MyDB()
    records = db_conn.query('SELECT ex_id, name_of_ex, descr_of_ex, level_of_ex, type_of_ex, body_part, '
                            'number_of_points '
                            'FROM exercise ')

    if form.validate_on_submit():
        form.level.data = int(form.level.data)

        db_conn.query('UPDATE user_exercise SET user_id = DEFAULT, ex_id = %s, date_of_add = DEFAULT WHERE user_id = %s',
                      current_user.id)
        db_conn.db_commit()
        return redirect(url_for('exercises'))
    return render_template('exercises.html', title='Exercises', records=records)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
