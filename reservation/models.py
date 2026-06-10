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

    table = models.ForeignKey(RestaurantTable, on_delete=models.SET_NULL, related_name="reservations", null=True)
    guests = models.PositiveSmallIntegerField()

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reservations")