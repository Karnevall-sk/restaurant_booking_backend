from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from .models import MenuCategory, MenuItem
from .serializers import MenuItemSerializer, MenuCategorySerializer

from restaurants.cache import restaurant_menu_cache

class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.prefetch_related(
        'menu_items')
    serializer_class = MenuCategorySerializer

    def perform_create(self, serializer):
        category = serializer.save()
        restaurant_menu_cache.invalidate(restaurant_id=category.restaurant_id)
    
    def perform_update(self, serializer):
        category = serializer.save()
        restaurant_menu_cache.invalidate(restaurant_id=category.restaurant_id)
    
    def perform_destroy(self, instance):
        restaurant_id = instance.restaurant_id
        instance.delete()
        restaurant_menu_cache.invalidate(restaurant_id=restaurant_id)



class MenuItemFilter(FilterSet):

    restaurant = django_filters.NumberFilter(field_name="category__restaurant_id")
    
    class Meta:
        model = MenuItem
        fields = {
                "category": ["exact"],
                "price": ["gte", "lte"],
                "is_available": ["exact"],
            }
    
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related(
        'category',
        'category__restaurant'
    )
    serializer_class = MenuItemSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter, 
        OrderingFilter]
    
    filterset_class  = MenuItemFilter
    search_fields = ['name', 'description']

    
    ordering_fields = ["price", "name"]

    def perform_create(self, serializer):
        item = serializer.save()
        restaurant_menu_cache.invalidate(restaurant_id=item.category.restaurant_id)
    
    def perform_update(self, serializer):
        item = serializer.save()
        restaurant_menu_cache.invalidate(restaurant_id=item.category.restaurant_id)
    
    def perform_destroy(self, instance):
        restaurant_id = instance.category.restaurant_id
        instance.delete()   
        restaurant_menu_cache.invalidate(restaurant_id=restaurant_id)

