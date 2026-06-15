from django.db import models
from restaurants.models import RestaurantTable, Restaurant
from users.models import User
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError

class Reservation(models.Model):
    
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.PROTECT,
        related_name="reservations")

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    table = models.ForeignKey(
        RestaurantTable, 
        on_delete=models.SET_NULL, 
        related_name="reservations", null=True)
    
    guests = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),]
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


    status = models.CharField(
        max_length=30, 
        choices=STATUS_CHOICES, 
        default="pending")

    comment = models.TextField(blank=True)

    user = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name="reservations")
    
    customer_name = models.CharField(
        max_length=255,
        default=""
    )

    customer_phone = PhoneNumberField()

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(
                "End time must be after start time"
            )

        if (
            self.table
            and self.guests > self.table.seats
        ):
            raise ValidationError(
                "Too many guests for selected table"
            )

    class Meta:
        indexes = [
            models.Index(fields=["restaurant", "start_time"]),
        ]