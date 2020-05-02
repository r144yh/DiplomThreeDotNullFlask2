from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from config import Config
from forms import LoginForm, RegistrationForm
from models import User, MyDB
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask('__main__',
            template_folder='frontend/templates',
            static_folder='frontend/static',
            static_url_path='')
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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
        db_conn.query('INSERT INTO uuser(user_id, username, email, ppassword) '
                      'VALUES(DEFAULT, %s, %s, %s)',
                      (form.username.data, form.email.data, hash_password))
        db_conn.db_commit()
        return redirect(url_for('login'))
    return render_template('registration.html', title='Registration', form=form)


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if current_user.id != user_id:
        return redirect(url_for('error_404'))
    db_conn = MyDB()
    records = db_conn.query('SELECT username, email, height, weight, level, count_of_tran '
                            'FROM uuser WHERE user_id = %s', (current_user.id,))
    return render_template('profile.html', title='Profile', records=records)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
