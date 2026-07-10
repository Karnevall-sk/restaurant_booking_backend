from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Restaurant, RestaurantTable, RestaurantWorkingHours, RestaurantClosure
from .serializers import *
from core.permissions import CanManageRestaurant
import datetime

from menu.serializers import MenuCategorySerializer
from reservations.services import get_availability

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
        
        availability = get_availability(
            restaurant,
            target_date,
        )

        return Response(availability)
    
    @action(
        detail=True,
        methods=["GET", "PATCH"],
        url_path="working-hours"
    )
    def working_hours(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == "GET":
            hours = RestaurantWorkingHours.objects.filter(
                restaurant=restaurant
            ).order_by("weekday")

            serializer = RestaurantWorkingHoursSerializer(hours, many=True)
            return Response(serializer.data)

        weekday = request.data.get("weekday")
        if weekday is None:
            return Response(
                {"detail": "weekday is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        working_day = get_object_or_404(
            RestaurantWorkingHours,
            restaurant=restaurant,
            weekday=weekday,
        )

        serializer = RestaurantWorkingHoursSerializer(
            working_day,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action == "working_hours" and self.request.method == "GET":
            return [CanManageRestaurant()]
        if self.action == "working_hours" and self.request.method == "PATCH":
            return [CanManageRestaurant()]
        return super().get_permissions()
        

class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.select_related(
        "restaurant")
    serializer_class = RestaurantTableSerializer



    