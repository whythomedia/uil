from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from flask_bootstrap import Bootstrap4
import modules.keys as keys
from modules.forms import RegistrationForm, LoginForm
from supabase import create_client, Client
import json

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
    data = supabase.table("student").select("*").execute()
    all_students = data.data  # Extract data
    return render_template('students.html', students=all_students)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        response = supabase.table("student").insert({
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

@app.route('/scoring')
def scoring():
    data = supabase.table("student").select("*").execute()
    students = data.data
    return render_template('scoring.html', students=students)

@app.route('/submit-scores', methods=['POST'])
def submit_scores():
    if not request.json:
        return jsonify({"error": "No data provided"}), 400

    scores = request.json
    scores_json = json.dumps(scores)
    user_email = session.get('email', "unknown user")
    try:
        result = supabase.table("scoring").insert({
            "scores": scores_json, 
            "administrator": user_email
        }).execute()
        return jsonify({"status": "success", "details": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/competitions')
def competitions():
    try:
        data = supabase.table("competitions")\
                    .select("competition_id, name, date, competition_details( detail_id, grade, start_time, room)")\
                    .order("competition_id", desc=False)\
                    .execute()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    competitions_data = data.data
    from datetime import datetime

    # Example of adjusting the time format before sending it to the template
    for competition in competitions_data:
        for detail in competition['competition_details']:
            # Assuming detail['start_time'] is a string like '15:00:00'
            detail['start_time'] = datetime.strptime(detail['start_time'], '%H:%M:%S').strftime('%H:%M')
    return render_template('competitions.html', competitions=competitions_data)

@app.route('/update-competition-details', methods=['POST'])
def update_competition_details():
    # Extract data from POST request
    data = request.json
    competition_id = data.get('id')
    field = data.get('field')
    new_value = data.get('newValue')
    print(data)
    # Basic validation
    if not competition_id or not field or new_value is None:
        return jsonify({'error': 'Missing data for update'}), 400
    try:
        updated_rows = supabase.table('competition_details').update({field: new_value}).eq('detail_id', competition_id).execute()
        if updated_rows.error:
            return jsonify({'error': updated_rows.error.message}), 500
        return jsonify({'message': 'Update successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



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