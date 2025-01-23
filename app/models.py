from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import time
from datetime import datetime

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(128), nullable=True)  # Optional field
    email = db.Column(db.String(128), unique=True, nullable=True)  # Optional field
    phone_number = db.Column(db.String(20), nullable=True)  # Optional field
    dob = db.Column(db.Date, nullable=True)  # Optional field
    weight = db.Column(db.Float, nullable=True)  # Optional field
    height = db.Column(db.Float, nullable=True)  # Optional field
    pantry_items = db.relationship('PantryItem', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PantryItem(db.Model):
	__tablename__ = 'pantry_item'
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), index=True, nullable=False)
	brand = db.Column(db.String(64))
	category = db.Column(db.String(64), nullable=False) # 4 types of Carbs, Fruit + Vegetable, Protein, Fats
	used = db.Column(db.Boolean, default=False)
	out_of_stock = db.Column(db.Boolean, default=False)
	weight = db.Column(db.Float)
	expiration_date = db.Column(db.DateTime, nullable=False)
	added_date = db.Column(db.DateTime, default=datetime.utcnow)
	calories = db.Column(db.Float)
	nutrition_content = db.Column(db.Text)
	image_path = db.Column(db.String(256))
	image_urls = db.relationship('FoodImage', backref='food_id', lazy=True)
    
	def is_expired(self):
		return self.expiration_date.date() < datetime.utcnow().date()

	def is_near_expiry(self):
		return 0 < (self.expiration_date.date() - datetime.utcnow().date()).days <= 7
     
class FoodImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))  # For remote storage (e.g., S3 or URLs)
    image_path = db.Column(db.String(255))  # For local storage (e.g., /static/images/)
    pantry_item_id = db.Column(db.Integer, db.ForeignKey('pantry_item.id'), nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)  # Store ingredients as a JSON or comma-separated string
    steps = db.Column(db.Text, nullable=False)  # Store steps as a JSON or comma-separated string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Recipe {self.name}>"

    def __init__(self, name, ingredients, steps):
        self.name = name
        self.ingredients = ingredients
        self.steps = steps