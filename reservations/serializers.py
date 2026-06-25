from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(style={'input_type': 'text'})
    end_time = serializers.DateTimeField(style={'input_type': 'text'})
    class Meta:
        model = Reservation
        fields = "__all__"
