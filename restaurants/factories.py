import factory
import random
from datetime import time
from .models import Restaurant, RestaurantTable, RestaurantClosure, RestaurantWorkingHours


class RestaurantFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Restaurant
    
    name = factory.Faker("company")
    city = factory.Faker("city")
    address = factory.Faker("address")
    description = factory.Faker("text")



class RestaurantTableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RestaurantTable
    
    restaurant = factory.SubFactory(RestaurantFactory)
    name = factory.Sequence(lambda n: f"table: {n}")
    seats = factory.LazyFunction(lambda: random.choice([2, 2, 2, 4, 4, 6, 8]))
    

class RestaurantWorkingHoursFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RestaurantWorkingHours

    restaurant = factory.SubFactory(RestaurantFactory)
    weekday = factory.Sequence(lambda n: n % 7)
    open_time = time(10, 0)
    close_time = time(22, 0)
    is_day_off = False
    closes_next_day = False


class RestaurantClosureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RestaurantClosure

    restaurant = factory.SubFactory(RestaurantFactory)
    date = factory.Faker("future_date")
    reason = factory.Faker("sentence", nb_words=4)