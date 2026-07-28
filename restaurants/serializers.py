from rest_framework import serializers
from .models import Restaurant, RestaurantTable, RestaurantWorkingHours, RestaurantClosure

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'city', 'address', 'description', 'reservation_duration', 'created_at', 'is_active']


class RestaurantTableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = RestaurantTable
        fields = [
            'id',
            'restaurant', 
            'restaurant_name', 
            'name', 
            'seats',
        ]


class RestaurantWorkingHoursSerializer(serializers.ModelSerializer):
    weekday_name = serializers.CharField(
        source="get_weekday_display",
        read_only=True
    )

    class Meta:
        model = RestaurantWorkingHours
        fields = [
            "id",
            "restaurant",
            "weekday",
            "weekday_name",
            "open_time",
            "close_time",
            "is_day_off",
            "closes_next_day",
        ]

class RestaurantClosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantClosure
        fields = "__all__"