from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Restaurant, RestaurantTable
from .serializers import RestaurantSerializer, RestaurantTableSerializer

from menu.serializers import MenuCategorySerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["name"]
    filterset_fields = {
        "city": ["exact"],

    }

    @action(
        detail=True, 
        methods=["get"],
        url_path="menu")
    def menu(self, request, pk=None):

        restaurant = self.get_object()

        categories = restaurant.categories.prefetch_related("menu_items")

        serializer = MenuCategorySerializer(
            categories,
            many = True
        )

        return Response(serializer.data)
        

class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.select_related(
        "restaurant")
    serializer_class = RestaurantTableSerializer

    