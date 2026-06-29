from rest_framework import serializers
from .models import Restaurant, RestaurantTable

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'city', 'address', 'description', 'reservation_duration', 'created_at', 'is_active']


class RestaurantTableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = RestaurantTable
        fields = ['id','restaurant', 'restaurant_name', 'name', 'seats',]