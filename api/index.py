from flask import Flask, render_template, redirect, request, url_for, flash, session, g
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import Email

import modules.keys as keys
from modules.forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = keys.SECRET_KEY
HARDCODED_PASSWORD = keys.ADMIN_PASSWORD
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///localdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    registration_code = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_user():
    user_email = session.get('email', None)
    user = {'is_admin': False, 'email': ''}
    if user_email:
        user['is_admin'] = True
        user['email'] = user_email
    return dict(user=user)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/students')
def students():
    all_students = Student.query.all()  # Query all students
    return render_template('students.html', students=all_students)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_student = Student(
            name=form.name.data,
            grade=form.grade.data,
            registration_code=form.registration_code.data
        )
        db.session.add(new_student)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        flash('Please enter your credentials to login.', 'info')
    if form.validate_on_submit():
        if form.password.data == HARDCODED_PASSWORD:
            session['email'] = form.email.data  # Store the user's email in session
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    session.clear()  # This removes all items from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
