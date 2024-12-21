from app import application
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, CreateQuestionForm, ChallengeAnswerForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Food
from urllib.parse import urlparse, unquote
from app import db
from flask import request 
from app.serverlibrary import mergesort, EvaluateExpression, get_smallest_three 
from werkzeug.utils import secure_filename
import os
from datetime import datetime

@application.route('/')
@application.route('/index/')
@login_required
def index():
	prefix = application.wsgi_app.prefix[:-1]
	return render_template('index.html', title='Home', prefix=prefix)

@application.route('/login/', methods=['GET', 'POST'])
def login():
	prefix = application.wsgi_app.prefix[:-1]
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		if (request.args.get('next')) is None:
			next_page = None
		else:
			next_page = unquote(request.args.get('next'))

		if not next_page or urlparse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form, prefix=prefix)

@application.route('/logout/')
def logout():
	prefix = application.wsgi_app.prefix[:-1]
	logout_user()
	return redirect(url_for('index'))

@application.route('/register/', methods=['GET', 'POST'])
def register():
	prefix = application.wsgi_app.prefix[:-1]
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user.')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form, prefix=prefix)

application.config['UPLOAD_FOLDER'] = 'app/static/uploads'  # Directory to store the uploaded images
application.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}  # Allowed image file extensions
def allowed_file(filename):
	'''
	Check if the file has allowed extensions.
	'''
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in application.config['ALLOWED_EXTENSIONS']

@application.route('/upload', methods=['GET', 'POST'])
def upload_image():
	if not os.path.exists(application.config['UPLOAD_FOLDER']):
		os.makedirs(application.config['UPLOAD_FOLDER'])

	if request.method == 'POST':
		if 'file' not in request.files:
			return 'No file part', 400
		file = request.files['file']
		if file.filename == '':
			return 'No selected file', 400
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)
			file.save(filepath)
			# food = Food(
			# 	name="Granola Bar",
			# 	brand="Nature's Valley",
			# 	type="snack",
			# 	used=False,
			# 	out_of_stock=False,
			# 	weight=50.0,
			# 	expiry_date=datetime(2025, 12, 31),
			# 	calories_content=200.0,
			# 	nutrition_content="Protein: 5g, Carbs: 35g, Fats: 7g",
			# 	image_path=filepath
			# )
			# db.session.add(food)
			# db.session.commit()
			return redirect(url_for('uploaded_file', filename=filename))
	return render_template('upload.html')

@application.route('/uploads/<foodname>')
def uploaded_file(filename):
    return f"File uploaded successfully: <img src='/static/uploads/{filename}' />"

