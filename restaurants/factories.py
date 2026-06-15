import factory
import random

from .models import Restaurant, RestaurantTable


class RestaurantFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Restaurant
    
    name = factory.Faker("company")
    city = factory.Faker("city")
    address = factory.Faker("address")
    description = factory.Faker("text")

    @factory.post_generation
    def create_tables(self, create, extracted, **kwargs):
        if not create:
            return

        # Генерируем 10 столиков со своими номерами при создании ресторана
        for i in range(1, 11):
            RestaurantTableFactory(restaurant=self, name=f"Table №{i}")



class RestaurantTableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RestaurantTable
    
    restaurant = factory.SubFactory(RestaurantFactory)
    name = factory.Sequence(lambda n: f"table: {n}")
    seats = factory.LazyFunction(lambda: random.choice([2, 2, 2, 4, 4, 6, 8]))
    
    