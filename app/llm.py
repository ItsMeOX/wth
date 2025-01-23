
import google.generativeai as genai
import PIL.Image
import json

from typing import TypeAlias
from typing import Optional, Any    

Number: TypeAlias = int | float

GOOGLE_API_KEY = "AIzaSyDtQrDc1WkUJa_zE37JC9OB3KO_myqap4E"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

INFO_PROMPT = '''
You are an expert product analyzer. Your task is to analyze the image of a product and provide its description in JSON format with the following attributes:
1. **name**: The type of product, such as "rice" or "yoghurt".
2. **brand**: The brand of the product. If the brand is not visible or mentioned, set this value as `None`.
3. **type**: Categorize the product into one of these four types:
   - "Carbohydrates"
   - "Fruits and Vegetables"
   - "Protein"
   - "Fats"
4. **expiry_date**: The expiry date of the product in the format "YYYY-MM-DD". If the expiry date is not visible or mentioned, set this value as `None`.
5. **nutrition_content**: A brief description of the product's nutritional content, including key elements such as calories, protein, carbohydrates, fats, etc. If this information is not visible, set this value to `None`. 

    - If no nutritional content is provided, use your knowledge of typical nutritional values for similar products to fill in reasonable estimates. For example:
      - **Rice**: 100g of cooked white rice contains approximately 130 calories, 2.7g of protein, 28g of carbohydrates, and 0.3g of fat.
      - **Yoghurt**: 100g of plain yoghurt contains approximately 59 calories, 3.5g of protein, 4.1g of carbohydrates, and 3.3g of fat.
      - **Chicken breast**: 100g contains approximately 165 calories, 31g of protein, 0g of carbohydrates, and 3.6g of fat.

If the product is not recognized or is not food, set all values as `None`.

Return ouput in json format:
{name: name, brand: brand, type: type, expiry_date: expiry_date, nutrition_content: nutrition_content}

If the product is not recognized or that product is not food, set all values as `None`.
'''

def get_information_products(img, prompt = INFO_PROMPT) -> dict[str, any]:
    """Get information products from Gemini API."""
    print("Getting information products...")
    try:
        response = model.generate_content([prompt, img])
        text = response.text
        print(text)
        start_index = text.find('{')
        end_index = text.find('}') + 1
        json_str = text[start_index:end_index]
        try:
            product_info = json.loads(json_str)
            print(product_info)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        
        return product_info
    except Exception as e:
        raise ValueError(f"Error in get_information_products: {e}")
    

from datetime import datetime

class Food_Management:
    def __init__(self, info: dict[str, Any]):
        self._name = info['name']
        self._brand = info['brand']
        self._type = info['type']
        self._expiry_date = info['expiry_date']
        self._used: bool = False
        self._out_of_stock: bool = False
        self._images = None
        self._info = None
        self._added_date = datetime.now().date()

    # Property for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    # Property for brand
    @property
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, value):
        self._brand = value

    # Property for type
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    # Property for expiry_date
    @property
    def expiry_date(self):
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, value):
        self._expiry_date = value

    # Method to get product information
    def get_info(self):
        return {
            'name': self._name,
            'brand': self._brand,
            'type': self._type,
            'expiry_date': self._expiry_date,
            'info': self._info
        }

    # Property to calculate days until expiry
    @property
    def days_until_expiry(self):
        if self._expiry_date:
            expiry = datetime.strptime(self._expiry_date, '%Y-%m-%d').date()
            today = datetime.today().date()
            delta = (expiry - today).days
            return delta
        return None

    # Prperty to determine expiry status
    @property
    def expiry_status(self):
        days_left = self.days_until_expiry
        if days_left is not None:
            if days_left < 0:
                return 'Red'  # expired
            elif days_left <= 3:
                return 'Yellow'  # expiring soon
            else:
                return 'Green'  # long shelf life
        return 'Unknown expiry status'
    
    @property
    def used(self):
        return self._used
    
    @used.setter
    def used(self, value):
        self._used = value

    @property
    def out_of_stock(self):
        return self._out_of_stock
    
    @out_of_stock.setter
    def out_of_stock(self, value):
        self._out_of_stock = value

class Inventory_Management:
    def __init__(self):
        self.food_items: List[Food_Management] = []

    def add_food_item(self, food: Food_Management):
        """Add a Food_Management object to the inventory."""
        self.food_items.append(food)

    def sort_by_days_until_expiry(self):
        """Sort inventory by days left until expiry, ascending order."""
        self.food_items.sort(key=lambda food: (food.days_until_expiry or float('inf')))

    def sort_by_added_date(self):
        """Sort inventory by the date the food was added, ascending order."""
        self.food_items.sort(key=lambda food: food._added_date)

    def sort_by_category_and_expiry(self):
        """
        Groups food items by category and sorts each group by expiry date.
        
        Returns:
            Dict[str, List[Food_Management]]: Dictionary with categories as keys 
            and sorted food items as values.
        """
        categories = ["Carbohydrates", "Fruits and Vegetables", "Protein", "Fats"]
        sorted_items = {}
        
        for category in categories:
            sorted_items[category] = sorted(
                [item for item in self.food_items if item._type == category],
                key=lambda x: datetime.strptime(x._expiry_date, "%Y-%m-%d")
            )
        return sorted_items

    def display_category(self, category: str):
        """
        Displays all food items in the specified category in a readable format.
        """
        items_in_category = self.sort_by_category_and_expiry().get(category)
        if not items_in_category:
            print(f"No items found in the category: {category}")
        else:
            print(f"Food items in the category '{category}':")
            return [item.get_info() for item in items_in_category]

    def display_inventory(self):
        """Display the inventory in a readable format."""
        return [item.get_info() for item in self.food_items]

import time
class MealPlanner:
    def __init__(self, inventory: Inventory_Management):
        self.inventory = inventory
        self.selected_ingredients = {}  # Store selected Food_Management objects

    def pick_ingredients_by_category(self, category: str):
        
        sorted_items = self.inventory.sort_by_category_and_expiry()
        picked_ingredients = []

        if category not in sorted_items:
            print(f"Invalid category: {category}. Please choose a valid category.")
            return picked_ingredients

        items = sorted_items[category]
        print(f"\nCategory: {category}")
        if not items:
            print("No ingredients available in this category.")
            return picked_ingredients

        for i, item in enumerate(items, start=1):
            print(f"{i}. {item.get_info()}")
        time.sleep(1)

        while True:
            try:
                user_input = input(f"Enter the numbers of the ingredients you'd like to use from {category} (comma-separated): ").strip()
                if not user_input:
                    print("Input cannot be empty. Please enter valid indices.")
                    continue

                indices = [int(idx.strip()) for idx in user_input.split(",")]
                
                if any(idx < 1 or idx > len(items) for idx in indices):
                    print(f"Some indices are out of range. Please enter indices between 1 and {len(items)}.")
                    continue

                # Add selected Food_Management objects to the list
                picked_ingredients = [items[idx - 1] for idx in indices]
                break  # Exit loop if everything is valid

            except ValueError:
                print("Invalid input. Please enter numbers only, separated by commas.")


        # Add the selected ingredients to the selected_ingredients list
        self.selected_ingredients[category] = picked_ingredients
        
        print(f"\nSelected ingredients from the category '{category}':")
        picked_ingredients = [item.get_info() for item in picked_ingredients]
        print(picked_ingredients)
        
    
    def __str__(self):
        if not self.selected_ingredients:
            return "No ingredients selected yet."

        result = "Ingredients Provided:\n"
        for category in self.selected_ingredients:
            result += f"- {category}: "
            ingredients = self.selected_ingredients[category]
            result += "\n"
            if ingredients:
                result += ", ".join(
                    f"{ingredient._name} ({ingredient._brand if ingredient._brand else 'No Brand'}, expiry: {ingredient._expiry_date})"
                    for ingredient in ingredients
                )
            else:
                result += "No ingredients selected"
            result += "\n"
        
        return result

class MasterChef:
    def __init__(self, meal_planner: MealPlanner):
        self.meal_planner = meal_planner
        
        system_prompt = f"""
            You are a professional chef specializing in creating simple, nutritious meals. Use the following ingredients from the customer's fridge to assist them:

            {str(meal_planner)}

            Your tasks:
            1. Suggest recipes using only these ingredients, be careful with the expiry dates of these ingredients.
            2. Provide clear, step-by-step cooking instructions when asked.
            3. Adapt recipes to user preferences or constraints during the chat.
            4. Be user-friendly and engaging to keep the customer interested with your suggestions.

            Do not introduce ingredients outside this list. Keep track of the conversation history to continue assisting seamlessly.
            If the customer do not have enough ingredients, suggest them to buy the missing ingredients.
            """

        self.model = genai.GenerativeModel(
            "models/gemini-1.5-flash",
            system_instruction=system_prompt
        )
        self.chat = self.model.start_chat(history=[])

