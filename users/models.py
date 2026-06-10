from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("The phone number must be set")

        user = self.model(phone=phone, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role","admin")

        return self.create_user(phone, password, **extra_fields)
    


class User(AbstractBaseUser,PermissionsMixin):
    
    ROLE_CHOICES = [ ("customer", "Customer"), 
                    ("manager", "Manager"), 
                    ("admin", "Admin"), ]
    
    phone = PhoneNumberField(unique=True, 
                             error_messages={
        "invalid": "Введите корректный номер телефона",
        "unique": "Пользователь уже существует"
        })
    name = models.CharField(max_length=255)

    email = models.EmailField(blank=True,null=True)

    role = models.CharField(max_length=100,choices=ROLE_CHOICES,default="customer")

    is_active = models.BooleanField(default=True) 
    is_staff = models.BooleanField(default=False) 

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self): 
        return str(self.phone)