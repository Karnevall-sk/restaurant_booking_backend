from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=255)

    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    description = models.CharField(max_length=255)

class RestaurantTable(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="tables")

    number = models.IntegerField()
    seats = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.restaurant.name} - table {self.number}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields=["restaurant", "number"],
            name="unique_table_per_restaurant"
            )
        ]
        