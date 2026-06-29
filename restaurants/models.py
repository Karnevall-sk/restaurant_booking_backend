from django.db import models
from django.core.exceptions import ValidationError


class Restaurant(models.Model):
    name = models.CharField(max_length=255)

    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    reservation_duration =models.PositiveSmallIntegerField(default=120)

    def get_working_hours(self, weekday:int):
        return self.working_hours.get(weekday=weekday)

    def __str__(self):
        return self.name

class RestaurantTable(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="tables")

    name = models.CharField(max_length=100, verbose_name="Название столика")
    seats = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.name} - restaurant: {self.restaurant_id}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields=["restaurant", "name"],
            name="unique_table_per_restaurant"
            )
        ]
        

class RestaurantWorkingHours(models.Model):

    WEEKDAYS = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
        (5, "Суббота"),
        (6, "Воскресенье"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="working_hours"
    )

    weekday = models.IntegerField(choices=WEEKDAYS)

    open_time = models.TimeField()
    close_time = models.TimeField()

    is_day_off = models.BooleanField(default=False)
    # if working after 00:00
    closes_next_day = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "weekday"],
                name="unique_working_hours_per_day"
            )
        ]
        ordering = ["weekday"]
    
    def clean(self):
        if self.is_day_off:
            if self.open_time or self.close_time:
                raise ValidationError("Can't be open in day off")
        else:
            if not self.open_time or not self.close_time:
                raise ValidationError(
                    "Please indicate opening and closing times, or weekend hours."
                )
            if not self.closes_next_day and self.open_time >= self.close_time:
                raise ValidationError(
                    "Opening time must be before closing time."
                    "If the restaurant is open after midnight, enable closes_next_day."
                )
    
    def __str__(self):
        day_name = dict(self.WEEKDAYS).get(self.weekday, self.weekday)
        if self.is_day_off:
            return f"{self.restaurant} — {day_name}: day off"
        return f"{self.restaurant} — {day_name}: {self.open_time:%H:%M}–{self.close_time:%H:%M}"