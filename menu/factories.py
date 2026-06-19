import factory

from .models import MenuCategory, MenuItem
from restaurants.factories import RestaurantFactory

from factory.django import ImageField

class MenuCategoryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = MenuCategory

    name = factory.Faker("word")
    restaurant = factory.SubFactory(RestaurantFactory)

class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuItem

    category = factory.SubFactory(MenuCategoryFactory)
    name = factory.Faker("word")
    description = factory.Faker("sentence", nb_words=10)
    price = "12.50"

    image = ImageField(color="blue")