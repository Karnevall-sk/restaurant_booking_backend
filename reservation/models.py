from django.db import models
from restaurants.models import RestaurantTable, Restaurant
from users.models import User

class Reservation(models.Model):
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    table = models.ForeignKey(RestaurantTable)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reservations")