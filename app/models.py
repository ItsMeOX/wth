from app import db
from app import login
from datetime import datetime 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(UserMixin, db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	def __repr__(self):
		return f'<User {self.username:}>'
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
class Food(db.Model):
	__tablename__ = 'food'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), index=True, nullable=False)
	brand = db.Column(db.String(64))
	type = db.Column(db.String(64), nullable=False)
	used = db.Column(db.Boolean)
	out_of_stock = db.Column(db.Boolean)
	weight = db.Column(db.Float)
	expiry_date = db.Column(db.DateTime, nullable=False)
	added_date = db.Column(db.DateTime)
	calories_content = db.Column(db.Float)
	nutrition_content = db.Column(db.Text)
