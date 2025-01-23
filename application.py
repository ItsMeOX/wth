from app import application, db
from app.models import User, PantryItem, FoodImage, Recipe

@application.shell_context_processor
def make_shell_context():
	return {'db': db, 'User': User, 'PantryItem': PantryItem,
			'FoodImage': FoodImage,
			'Recipe': Recipe}

if __name__ == "__main__":
	application.run(host="0.0.0.0", port=8080, debug=True)
