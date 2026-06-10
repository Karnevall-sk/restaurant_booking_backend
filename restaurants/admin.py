from django.contrib import admin
from .models import Restaurant, RestaurantTable

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Restaurant._meta.fields]


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RestaurantTable._meta.fields]