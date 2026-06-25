from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from .models import MenuCategory, MenuItem
from .serializers import MenuItemSerializer, MenuCategorySerializer

class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.prefetch_related(
        'menu_items')
    serializer_class = MenuCategorySerializer



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

