from django.db import models
from restaurants.models import Restaurant

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant)
    name = models.CharField(max_length=255)


class MenuCategory(models.Model):
    name = models.CharField(max_length=255)
    restaraunt = models.ForeignKey('restaurants.Restauraut')