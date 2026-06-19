from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=255)

    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

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

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="working_hours"
    )

    weekday = models.IntegerField()

    open_time = models.TimeField()
    close_time = models.TimeField()