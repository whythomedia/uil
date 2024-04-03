from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from api.forms import RegistrationForm
import api.keys as keys

app = Flask(__name__)
app.secret_key = keys.SECRET_KEY
Bootstrap(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Extracting data from the form
        name = form.name.data
        grade = form.grade.data
        registration_code = form.registration_code.data

        # Printing form data to the console
        print(f'Name: {name}, Grade: {grade}, Registration Code: {registration_code}')

        # Flash message or other form of user feedback
        flash('Registration successful!', 'success')

        # Redirecting to prevent form resubmission
        return redirect(url_for('register'))

    return render_template('register.html', form=form)