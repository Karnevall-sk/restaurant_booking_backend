from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "name",
            "email",
            "role",
            "restaurant",
            "is_verified",
            "created_at",
        )
        read_only_fields = fields


class UpdateMeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "name",
            "email",
        )