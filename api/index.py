from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_bootstrap import Bootstrap4
import modules.keys as keys
from modules.forms import RegistrationForm, LoginForm
from supabase import create_client, Client

app = Flask(__name__)
app.config['SECRET_KEY'] = keys.SECRET_KEY
HARDCODED_PASSWORD = keys.ADMIN_PASSWORD

Bootstrap4(app)

# Initialize Supabase client
url: str = keys.SUPABASE_URL
key: str = keys.SUPABASE_KEY
supabase: Client = create_client(url, key)

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
    data = supabase.table("Student").select("*").execute()
    all_students = data.data  # Extract data
    return render_template('students.html', students=all_students)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        response = supabase.table("Student").insert({
            "name": form.name.data,
            "grade": form.grade.data,
            "registration_code": form.registration_code.data
        }).execute()
        
        # Check for errors in the response
        if 'error' in response and response['error'] is not None:
            flash('Registration failed: ' + str(response['error']), 'danger')
        else:
            flash('Registration successful!', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        flash('Please enter your credentials to login.', 'info')
    if form.validate_on_submit():
        user_exists = True#check_user_exists(form.email.data)  # Implement check_user_exists
        if user_exists and form.password.data == HARDCODED_PASSWORD:
            session['email'] = form.email.data
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        elif not user_exists:
            flash('Email address not found.', 'danger')
        else:
            flash('Login Unsuccessful. Please check your email and password.', 'danger')
    else:
        # This will run if the form does not validate (i.e., incorrect email format, missing fields, etc.)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f'{fieldName}: {err}', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    session.clear()  # This removes all items from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
