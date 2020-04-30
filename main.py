from flask import Flask, render_template, flash, redirect, url_for
from config import Config
from forms import LoginForm, RegistrationForm

app = Flask('__main__',
            template_folder='frontend/templates',
            static_folder='frontend/static',
            static_url_path='')
app.config.from_object(Config)


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('main'))
    return render_template('login.html', title='Вход', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Welcome, Chicken')
        return redirect(url_for('index'))
    return render_template('registration.html', title='Registration', form=form)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
