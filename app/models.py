from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import time
from datetime import datetime

@login.user_loader
def load_user(id):
    """
    Flask-Login function to load a user by their ID.
    """
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
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
	category = db.Column(db.String(64), nullable=False) # Carbs, Protein, etc.
	used = db.Column(db.Boolean, default=False)
	out_of_stock = db.Column(db.Boolean, default=False)
	weight = db.Column(db.Float)
	expiration_date = db.Column(db.DateTime, nullable=False)
	added_date = db.Column(db.DateTime, default=time.time)
	calories = db.Column(db.Float)
	nutrition_content = db.Column(db.Text)
	image_path = db.Column(db.String(256))
    
	def is_expired(self):
		return self.expiration_date < datetime.utcnow().date()

	def is_near_expiry(self):
		return 0 <= (self.expiration_date - datetime.utcnow().date()).days <= 7

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Recipe {self.name}>'
