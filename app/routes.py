from app import application
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, PantryItem, Recipe
from urllib.parse import urlparse, unquote
from app import db
from flask import request 
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta

@application.route('/')
@application.route('/index/')
@login_required
def index():
	prefix = application.wsgi_app.prefix[:-1]
	return render_template('index.html', title='Home', prefix=prefix)

@application.route('/login/', methods=['GET', 'POST'])
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
    print(items[0].name)
    return render_template('inventory.html', title='Inventory', items=items)

def get_ai_recipe_suggestions(selected_items):
    """
    Replace this function with actual AI logic or API integration to suggest recipes.
    """
    # Mock data for demo purposes
    return [
        {
            "id": 1,
            "name": "Spaghetti Bolognese",
            "image_url": "https://example.com/spaghetti.jpg",
            "ingredients": ["spaghetti", "ground beef", "tomato sauce"],
            "steps": ["Boil spaghetti", "Cook ground beef", "Mix with sauce"]
        },
        {
            "id": 2,
            "name": "Chicken Salad",
            "image_url": "https://example.com/salad.jpg",
            "ingredients": ["chicken", "lettuce", "olive oil"],
            "steps": ["Grill chicken", "Chop lettuce", "Mix with dressing"]
        }
    ]

@application.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        recipe =get_ai_recipe_suggestions(selected_items)
        return render_template('recipe.html', recipe=recipe)
    items = PantryItem.query.filter_by(owner=current_user).all()
    return render_template('recipes.html', title='Recipe Suggestion', items=items)


@application.route('/recipe/<int:id>')
@login_required
def recipe(id):
    # Mock fetching the recipe by ID (replace with actual database query if needed)
    suggested_recipes = get_ai_recipe_suggestions([])  # Mocked suggestions
    recipe = next((r for r in suggested_recipes if r["id"] == id), None)
    
    if not recipe:
        flash("Recipe not found.")
        return redirect(url_for('recipes'))
    
    return render_template('recipe.html', recipe=recipe)

@application.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html', user=current_user)

@application.route('/home')
@login_required
def home():
    # Fetch pantry item data for the current user
    total_items = PantryItem.query.filter_by(owner=current_user).count()
    expiring_items = PantryItem.query.filter_by(owner=current_user).filter(PantryItem.expiration_date <= datetime.now() + timedelta(days=7)).count()
    expired_items = PantryItem.query.filter_by(owner=current_user).filter(PantryItem.expiration_date < datetime.now()).count()

    # Fetch a list of recipes (this part assumes you have a Recipe model, adjust as needed)
    recipes = Recipe.query.all()  # Replace with your logic to get relevant recipes
    
    # Pass the data to the template
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
			new_item = PantryItem(
				name="Gronola",
				brand="no brand",
				category="dessert",
				used=False,
				out_of_stock=False,
				weight=120.0,
				expiration_date=datetime(2025, 6, 27),
				calories=520.0,
				nutrition_content="Protein: 110g, Carbs: 97g, Fats: 10g",
				image_path=filepath, 
                user_id=current_user.id
			)
			db.session.add(new_item)
			db.session.commit()
			return redirect(url_for('uploaded_file', foodname=new_item.name))
	return render_template('upload.html')

@application.route('/uploads/<foodname>')
def uploaded_file(foodname):
    food = PantryItem.query.filter_by(name = foodname).first()
    image_path = food.image_path
    if image_path.startswith('app'):
        image_path = image_path[3:]
    print(image_path)
    return f"File uploaded successfully: <img src='{image_path}' />"
