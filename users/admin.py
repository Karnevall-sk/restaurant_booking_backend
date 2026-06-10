from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from django import forms

from .models import User

class CustomUserCreationForm(UserCreationForm):

    def clean_email(self):
        raise forms.ValidationError("МОЯ ФОРМА РАБОТАЕТ")


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        "id",
        "phone",
        "name",
        "email",
        "role",
        "is_verified",
        "is_staff",
        "is_active",
        "created_at",
    )

    add_form = CustomUserCreationForm

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal info", {"fields": ("name", "email", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")}),
    )

    list_filter = ("role", "is_staff", "is_active", "is_verified")
    
    search_fields = ("phone", "name", "email")

    add_fieldsets = (
        (
            "None",
            {
                "classes": ("toggle",),
                "fields": ("phone", "password1", "password2", "name", "email", "role", "is_staff", "is_active"),
            },
        ),)

    ordering = ("-created_at",)

    

