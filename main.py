from flask import Flask, render_template
from flask_material import Material
from config import Config
from forms import LoginForm

app = Flask('__main__', template_folder='frontend/templates')
app.config.from_object(Config)
Material(app)


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Вход', form=form)


if __name__ == '__main__':
    app.run(debug=True)
