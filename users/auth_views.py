from rest_framework_simplejwt.views import TokenObtainPairView

from .auth_serializers import PhoneTokenObtainPairSerializer


class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer