from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import MenuCategory, MenuItem
from .serializers import MenuItemSerializer, MenuCategorySerializer

class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.prefetch_related(
        'menu_items')
    serializer_class = MenuCategorySerializer

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = {
        'category': ["exact"],
        'price': ['gte','lte']
    }
    
    ordering_fields = ["price", "name"]