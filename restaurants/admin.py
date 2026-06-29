from django.contrib import admin
from .models import *

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Restaurant._meta.fields]


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RestaurantTable._meta.fields]

@admin.register(RestaurantWorkingHours)
class RestaurantWorkingHoursAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RestaurantWorkingHours._meta.fields]