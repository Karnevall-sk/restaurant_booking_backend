from restaurants.factories import RestaurantFactory, RestaurantTableFactory


def seed_restaurants(count=10):

    restaurants = RestaurantFactory.create_batch(count)

    for restaurant in restaurants:
        for i in range(1, 11):
            RestaurantTableFactory(
                restaurant=restaurant,
                name=f"Table №{i}"
            )