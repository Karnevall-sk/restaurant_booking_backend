from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, RestaurantTableViewSet

router = DefaultRouter()
router.register("restaurants", RestaurantViewSet, basename="restaurant")
router.register("tables", RestaurantTableViewSet, basename='table')

urlpatterns = [
    path('', include(router.urls)), 
]
