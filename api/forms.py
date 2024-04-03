from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    grade = IntegerField('Grade', validators=[DataRequired()])
    registration_code = StringField('Registration Code', validators=[DataRequired()])
    submit = SubmitField('Register')
