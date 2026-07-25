from rest_framework import serializers
from .models import Reservation
from .services import create_reservation

class ReservationSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(style={'input_type': 'text'})
    end_time = serializers.DateTimeField(
    read_only=True,
    style={"input_type": "text"},
    )
    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = (
            "status",
            "end_time",
            "created_at",
            
        )

    def create(self, validated_data):
        return create_reservation(**validated_data)