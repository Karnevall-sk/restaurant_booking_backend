from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuCategoryViewSet, MenuItemViewSet

router = DefaultRouter()
router.register('menu-category', MenuCategoryViewSet, basename='menu-category')
router.register("menu-items", MenuItemViewSet, basename="menu-items"
)
urlpatterns = [
    path('', include(router.urls)),
]