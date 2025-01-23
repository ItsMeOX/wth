from app import application
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, ProfileUpdateForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, PantryItem, Recipe, FoodImage
from urllib.parse import urlparse, unquote
from app import db
from flask import request 
from werkzeug.utils import secure_filename
import os, sys
from threading import Thread
from datetime import datetime, timedelta, time
from app.llm import *
import json

@application.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		return redirect(url_for('home'))
	return render_template('login.html', title='Sign In', form=form)

@application.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@application.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

@application.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
	if request.method == 'POST':
		item = PantryItem(
			name=request.form['name'],
			category=request.form['category'],
			weight=request.form['weight'],
			expiration_date=datetime.strptime(request.form['expiration_date'], '%Y-%m-%d').date(),
			calories=request.form['calories'],
			owner=current_user
		)
		db.session.add(item)
		db.session.commit()
		flash('Item added successfully!')
	items = PantryItem.query.filter_by(user_id=current_user.id).all()
	return render_template('inventory.html', title='Inventory', items=items)

@application.route('/food/<int:food_id>')
def food_detail(food_id):
	food_item = PantryItem.query.get_or_404(food_id)
	print(len(food_item.image_urls))
	for image in food_item.image_urls:
		print(image.image_url)
	return render_template('food_detail.html', title=food_item.name, food=food_item)

def get_ai_recipe_suggestions(selected_items: list[str]) -> list[dict[str, Any]]:
	"""
	Generate AI-based recipe suggestions using selected items.
	
	Args:
		selected_items (List[str]): A list of ingredient names.

	Returns:
		List[Dict[str, Any]]: A list of recipes, each with a name, image URL, ingredients, and steps.
	"""
	if not selected_items:
		return []

	# Prepare the input prompt for the AI model
	if not selected_items:
		return []

	# Prepare the input prompt for the AI model
	ingredients_list = ', '.join(selected_items)
	prompt = f"""
	You are a professional chef. Suggest creative recipes using the following ingredients: {ingredients_list}.
	Return output as Json format following this example:
	[
		{{
			"name": "Recipe Name",
			"ingredients": ["ingredient1", "ingredient2"],
			"steps": ["step1", "step2"]
		}}
	]
	"""

	try:
		# Generate response using the AI model
		response = model.generate_content([prompt])

		text = response.text

		start_index = text.find('{')
		end_index = text.find('}') + 1
		json_text = text[start_index: end_index]

		print(json_text)

		# Parse and return recipes
		return parse_ai_response(json_text)

	except Exception as e:
		print(f"Error generating AI response: {e}")
		return []

def parse_ai_response(ai_response: str) -> list[dict[str, Any]]:
	"""
	Parse the AI-generated response into a structured recipe format.

	Args:
		ai_response (str): The raw text response from the AI model.

	Returns:
		List[Dict[str, Any]]: A list of parsed recipes.
	"""
	try:
		# Assuming AI provides JSON-like responses in text format
		recipes = json.loads(ai_response)

		# If the response is a single recipe, wrap it in a list
		if isinstance(recipes, dict):
			recipes = [recipes]

		# Validate the structure of the recipes
		if isinstance(recipes, list):
			for recipe in recipes:
				if not all(key in recipe for key in ["name", "ingredients", "steps"]):
					print(f"Invalid recipe structure: {recipe}")
					return []
			return recipes
		else:
			print("AI response is not a valid list of recipes.")
			return []

	except json.JSONDecodeError:
		print("Failed to decode AI response. Ensure the AI response is JSON formatted.")
		return []

@application.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
	if request.method == 'POST':
		selected_items = request.form.getlist('ingredients')  # Fetch selected ingredients
		recipes_data = get_ai_recipe_suggestions(selected_items)  # Call AI model with selected items
		# Save the recipe to the database
		# for recipe_data in recipes_data:
		print('recipes_data', recipes_data)
		name = recipes_data[0]["name"]
		ingredients = ', '.join(recipes_data[0]["ingredients"])  # Join ingredients into a string or JSON
		steps = '\n'.join(recipes_data[0]["steps"])  # Join steps into a string or JSON
		recipe = Recipe(name=name, ingredients=ingredients, steps=steps)
		db.session.add(recipe)
		db.session.commit()

		return redirect(f'recipe/{recipe.id}')

	# Group items by category
	items = PantryItem.query.filter_by(owner=current_user).all()
	categories = {
		"Carbs": [],
		"Fruit + Vegetable": [],
		"Proteins": [],
		"Fats": []
	}
	for item in items:
		if item.category in categories:
			categories[item.category].append(item)

	return render_template('recipes.html', title='Recipe Suggestion', categories=categories)

@application.route('/recipe/<int:id>')
@login_required
def recipe(id):
	recipe = Recipe.query.get_or_404(id)
	print('recipe', recipe)
	print(recipe.id, recipe.name)
	recipe.steps = recipe.steps.split('.')
	recipe.ingredients = recipe.ingredients.split(',')
	# suggested_recipes = get_ai_recipe_suggestions([])
	# recipe = next((r for r in suggested_recipes if r["id"] == id), None)
	
	if not recipe:
		flash("Recipe not found.")
		print("recipe not found")
		return redirect(url_for('recipes'))
	
	return render_template('recipe.html', recipe=recipe, title=recipe.name)

@application.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = ProfileUpdateForm()

	if form.validate_on_submit():
		current_user.full_name = form.full_name.data
		current_user.email = form.email.data
		current_user.phone_number = form.phone_number.data
		current_user.dob = form.dob.data
		current_user.weight = form.weight.data
		current_user.height = form.height.data

		db.session.commit()
		flash('Your profile has been updated!', 'success')
		return redirect(url_for('account'))

	# Pre-fill the form with current user data
	form.full_name.data = current_user.full_name
	form.email.data = current_user.email
	form.phone_number.data = current_user.phone_number
	form.dob.data = current_user.dob
	form.weight.data = current_user.weight
	form.height.data = current_user.height

	return render_template('account.html', title='Account', form=form)

@application.route('/')
@application.route('/home')
@login_required
def home():
	total_items = PantryItem.query.filter_by(owner=current_user).count()
	expiring_items = PantryItem.query.filter_by(owner=current_user).filter(PantryItem.expiration_date <= datetime.now() + timedelta(days=7)).all()
	expired_items = PantryItem.query.filter_by(owner=current_user).filter(PantryItem.expiration_date < datetime.now()).all()

	recipes = Recipe.query.all()
	
	return render_template('home.html', total_items=total_items, expiring_items=expiring_items, expired_items=expired_items, recipes=recipes, title='Home')

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
			filepath = filepath.replace('\\', '/')
			file.save(filepath)

			img = PIL.Image.open(filepath)
			
			if img.mode == 'RGBA':
				img = img.convert('RGB')

			if filepath.startswith("food"):
				filepath = filepath[4:]
			
			if(filepath.startswith('app')):
				filepath = filepath[3:]
			
			# Call the AI function to get product information
			product_info = get_information_products(img)
			print(product_info)
			if product_info is None or product_info['expiry_date'] is None:
				return render_template('upload.html', error='Product information not found. Please try again.')
			
			try:
				product_info['expiry_date'] = datetime.strptime(product_info['expiry_date'], '%Y-%m-%d')
			except ValueError:
				product_info['expiry_date'] = None
	
			# Save the image with the product's name
			new_filename = f"{product_info['name'].replace(' ', '_')}.jpg"
			new_filepath = os.path.join(application.config['UPLOAD_FOLDER'], new_filename)
			new_filepath = new_filepath.replace('\\', '/')
			img.save(new_filepath, "JPEG")

			# Save the product information to the database
			new_item = PantryItem(
				name= product_info['name'],
				brand= product_info['brand'],
				category= product_info['type'],
				used=False,
				out_of_stock=False,
				weight = 120.0,
				expiration_date= product_info['expiry_date'],
				calories=520.0,
				nutrition_content= product_info['nutrition_content'],
				image_path=new_filepath,
				user_id=current_user.id
			)
			db.session.add(new_item)
			db.session.commit()

			new_image = FoodImage(image_url=filepath, pantry_item_id=new_item.id)
			db.session.add(new_image)
			db.session.commit()
			
			return "Successfully Added!"
	return render_template('upload.html')

# @application.route('/uploads/<food_id>')
# def uploaded_file(food_id):
#     food = PantryItem.query.filter_by(id = food_id).first()
#     image_path = food.image_path
#     if image_path.startswith('app'):
#         image_path = image_path[3:]
#     print(image_path)
#     return f"File uploaded successfully: <img src='{image_path}' />"