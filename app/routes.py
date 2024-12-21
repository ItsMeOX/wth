from app import application
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse, unquote
from app.models import User, PantryItem, Recipe
from app import db
from flask import request
from datetime import datetime, timedelta

@application.route('/')
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
            expiration_date=datetime.strptime(request.form['expiration_date'], '%Y-%m-%d'),
            calories=request.form['calories'],
            owner=current_user
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!')
    items = PantryItem.query.filter_by(owner=current_user).all()
    return render_template('inventory.html', items=items)

def get_recipe_suggestion(selected_items):
    # Replace this with actual API call
    return {"name": "Spaghetti Bolognese", "ingredients": selected_items}

@application.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        recipe = get_recipe_suggestion(selected_items)
        return render_template('recipe.html', recipe=recipe)
    items = PantryItem.query.filter_by(owner=current_user).all()
    return render_template('recipes.html', items=items)

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
    return render_template('home.html', total_items=total_items, expiring_items=expiring_items, expired_items=expired_items, recipes=recipes)

