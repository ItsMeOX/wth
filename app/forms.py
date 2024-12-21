from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, FloatField, HiddenField, EmailField, DateField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Optional
from app.models import User

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', 
							   validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')

class ProfileUpdateForm(FlaskForm):
    full_name = StringField('Full Name', validators=[Optional()])
    email = EmailField('Email', validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    weight = FloatField('Weight (kg)', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional()])
    submit = SubmitField('Update Profile')