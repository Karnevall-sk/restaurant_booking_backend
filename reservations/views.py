from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsManagerOrAdmin

from .models import Reservation
from .serializers import ReservationSerializer
from reservations.services import create_reservation, confirm_reservation, cancel_reservation, complete_reservation

class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Reservation.objects.none()

        if user.role == "admin":
            return Reservation.objects.all().order_by("id")

        if user.role == "manager":
            return Reservation.objects.filter(
                restaurant=user.restaurant
            )

        return Reservation.objects.filter(
            user=user
        )

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsManagerOrAdmin],
        url_path="confirm"
    )
    def confirm(
        self,
        request,
        pk=None
    ):

        reservation = self.get_object()

        confirm_reservation(reservation)

        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"],
        detail=True,
        permission_classes = [IsManagerOrAdmin],
    )
    def cancel(
        self,
        request,
        pk=None
    ):
        reservation = self.get_object()

        cancel_reservation(reservation)

        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_200_OK,
        )
    
    @action(
        methods=["POST"],
        detail=True,
        permission_classes = [IsManagerOrAdmin],
    )
    def complete(
        self,
        request,
        pk=None
    ):
        reservation = self.get_object()

        complete_reservation(reservation)

        return Response(
            
            status=status.HTTP_200_OK,
        )



