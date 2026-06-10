from django.contrib import admin
from .models import *

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MenuCategory._meta.fields]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MenuItem._meta.fields]