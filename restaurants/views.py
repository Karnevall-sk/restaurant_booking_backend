from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Restaurant, RestaurantTable
from .serializers import RestaurantSerializer, RestaurantTableSerializer
import datetime

from menu.serializers import MenuCategorySerializer
from reservations.services import get_slots_for_date

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["name"]
    filterset_fields = {
        "city": ["exact"],

    }

    # api/v1/menu
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
    
    # api/v1/availability
    @action(
        detail=True,
        methods=["get"],
        url_path="availability"
    )
    def availability(self, request, pk):
        restaurant = self.get_object()

        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"detail": "Query parameter 'date' is required (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        slots = get_slots_for_date(restaurant, target_date)
        return Response({"date": date_str, "slots": slots})
        

class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.select_related(
        "restaurant")
    serializer_class = RestaurantTableSerializer




    