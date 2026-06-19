from rest_framework import serializers
from .models import MenuCategory, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = MenuItem
        fields = ['id','name', 'category', 'description', 'price', 'image', 'is_available']

class MenuCategorySerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'restaurant', 'menu_items']