from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Restaurant, RestaurantTable, RestaurantWorkingHours, RestaurantClosure
from .serializers import *
from core.permissions import CanManageRestaurant
from .cache import (
    restaurant_list_cache,
    restaurant_menu_cache,
    restaurant_availability_cache
)

import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

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

    def list(self, request, *args, **kwargs):

        if request.query_params:
            return super().list(request, *args, **kwargs)


        data = restaurant_list_cache.get_or_set(
            fetch_func=lambda: super(RestaurantViewSet, self).list(request, *args, **kwargs).data
        )
        return Response(data)

    def perform_create(self, serializer):
        restaurant = serializer.save()
        restaurant_list_cache.invalidate()

    def perform_update(self, serializer):
        restaurant = serializer.save()
        restaurant_list_cache.invalidate()

    def perform_destroy(self, instance):
        instance.delete()   
        restaurant_list_cache.invalidate()

    # /api/v1/restaurants/id/menu/
    @action(
        detail=True, 
        methods=["get"],
        url_path="menu")
    def menu(self, request, pk=None):

        def fetch_menu():
            restaurant = self.get_object()
            categories = restaurant.categories.prefetch_related("menu_items")
            return MenuCategorySerializer(categories, many=True).data

        data = restaurant_menu_cache.get_or_set(
            fetch_func=fetch_menu,
            restaurant_id=pk
        )

        return Response(data)
    
    # api/v1/availability
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Reservation date"
            )
        ]
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="availability"
    )
    def availability(self, request, pk):

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

        def fetch_availability():
            restaurant = self.get_object()
            availability = get_availability(
                restaurant,
                target_date,)
            return availability
        
        data = restaurant_availability_cache.get_or_set(
            fetch_func=fetch_availability,
            restaurant_id=pk,
            date=target_date
        )

        return Response(data)
    
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

        restaurant_availability_cache.invalidate_pattern(
            restaurant_id=restaurant.id,
            )

        return Response(serializer.data)

    
    def get_permissions(self):
        if self.action == "working_hours" and self.request.method == "GET":
            return [AllowAny()]
        if self.action == "working_hours" and self.request.method == "PATCH":
            return [CanManageRestaurant()]
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [CanManageRestaurant()]
        

class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.select_related(
        "restaurant")
    serializer_class = RestaurantTableSerializer


class RestaurantClosureViewSet(viewsets.ModelViewSet):
    queryset = RestaurantClosure.objects.select_related("restaurant")
    serializer_class = RestaurantClosureSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "restaurant": ["exact"],
        "date": ["exact", "gte", "lte"],
    }

    permission_classes = [CanManageRestaurant]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == "admin":
            return queryset

        return queryset.filter(
            restaurant=user.restaurant
        )

    def perform_create(self, serializer):
        closure = serializer.save()

        restaurant_availability_cache.invalidate_pattern(
            restaurant_id=closure.restaurant_id
        )

    def perform_update(self, serializer):
        closure = serializer.save()

        restaurant_availability_cache.invalidate_pattern(
            restaurant_id=closure.restaurant_id
        )

    def perform_destroy(self, instance):
        restaurant_id = instance.restaurant_id

        instance.delete()

        restaurant_availability_cache.invalidate_pattern(
            restaurant_id=restaurant_id
        )
    