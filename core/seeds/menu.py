from menu.factories import MenuItemFactory, MenuCategoryFactory
from restaurants.models import Restaurant
import random

MENU_DATA = {
    "Pizza": [
        "Margherita",
        "Pepperoni",
        "Four Cheese",
        "Hawaiian",
        "Meat Lovers",
        "BBQ Chicken",
        "Carbonara Pizza",
    ],

    "Burgers": [
        "Classic Burger",
        "Cheeseburger",
        "Big Burger",
        "Double Cheeseburger",
        "BBQ Burger",
        "Spicy Burger",
    ],

    "Appetizers": [
        "French Fries",
        "Potato Wedges",
        "Onion Rings",
        "Mozzarella Sticks",
        "Chicken Nuggets",
        "BBQ Wings",
    ],

    "Salads": [
        "Chicken Caesar Salad",
        "Greek Salad",
        "Olivier Salad",
        "Warm Beef Salad",
        "Tuna Salad",
    ],

    "Soups": [
        "Borscht",
        "Solyanka",
        "Chicken Soup",
        "Mushroom Cream Soup",
        "Tomato Soup",
    ],

    "Main Courses": [
        "Ribeye Steak",
        "Grilled Salmon",
        "Teriyaki Chicken",
        "Pasta Carbonara",
        "Pasta Bolognese",
        "Beef Stroganoff",
        "Pork Kebab",
    ],

    "Desserts": [
        "Cheesecake",
        "Tiramisu",
        "Honey Cake",
        "Chocolate Lava Cake",
        "Ice Cream",
        "Napoleon Cake",
    ],

    "Drinks": [
        "Coca-Cola",
        "Sprite",
        "Orange Juice",
        "Apple Juice",
        "Americano",
        "Cappuccino",
        "Latte",
        "Black Tea",
        "Green Tea",
    ],
}

PRICE_RANGES = {
    "Pizza": (2500, 6000),
    "Burgers": (2000, 4500),
    "Appetizers": (1000, 3000),
    "Salads": (1800, 4000),
    "Soups": (1500, 3500),
    "Main Courses": (3000, 9000),
    "Desserts": (1200, 3500),
    "Drinks": (500, 2500),
}

def seed_menu():

    restaurants = list(Restaurant.objects.all())

    category_names = list(MENU_DATA.keys())

    for restaurant in restaurants:

        num_categories = random.randint(3,len(MENU_DATA))
        
        chosen_categories = random.sample(
            category_names,
            k=num_categories
        )

        for category_name  in chosen_categories:

            menu_category = MenuCategoryFactory(
                name = category_name,
                restaurant = restaurant
            )


            num_menu_items = random.randint(3,len(MENU_DATA[category_name]))
            menu_items = random.sample(MENU_DATA[category_name], k=num_menu_items)
            for menu_item in menu_items:
                min_price, max_price = PRICE_RANGES[category_name]
                MenuItemFactory(
                    category = menu_category,
                    name = menu_item,
                    price=random.randint(
                        min_price,
                        max_price
                    )
                )