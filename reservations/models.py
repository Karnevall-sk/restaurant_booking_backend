from django.db import models
from django.db.models import Func
from restaurants.models import RestaurantTable, Restaurant
from users.models import User
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators, RangeBoundary, DateTimeRangeField
from django.db.models import Q

from datetime import timedelta

class TsTzRange(Func):
    function = "TSTZRANGE"
    output_field = DateTimeRangeField()

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
    end_time = models.DateTimeField(editable=False)


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
    
    def save(self, *args, **kwargs):
        if self.start_time and self.restaurant_id:
            duration = self.restaurant.reservation_duration
            self.end_time = self.start_time + timedelta(minutes=duration)
        super().save(*args, **kwargs)

    def clean(self):

        if self.table and self.guests is not None:
            if self.guests > self.table.seats:
                raise ValidationError(
                    "Too many guests for selected table"
                )

    class Meta:
        indexes = [
        models.Index(fields=["restaurant", "start_time"]),
        ]
        constraints = [
            ExclusionConstraint(
                name="no_overlapping_reservations",
                expressions=[
                    (TsTzRange("start_time", "end_time", RangeBoundary()), RangeOperators.OVERLAPS),
                    ("table", RangeOperators.EQUAL),
                ],
                condition=Q(status__in=["pending", "confirmed"]),
            )
        ]

