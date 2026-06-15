from restaurants.factories import RestaurantFactory

def seed_restaurants(restaurant_count = 10):
    RestaurantFactory.create_batch(restaurant_count)

        