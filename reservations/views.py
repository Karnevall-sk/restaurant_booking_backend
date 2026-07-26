from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsManagerOrAdmin, CanCancelReservation

from .filters import ReservationFilter
from .models import Reservation
from .serializers import ReservationSerializer
from core.pagination import DefaultPagination
from reservations.services import create_reservation, confirm_reservation, cancel_reservation, complete_reservation

from restaurants.cache import restaurant_availability_cache

class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.select_related("restaurant", "table", "user").order_by("-start_time")
    serializer_class = ReservationSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = ReservationFilter

    pagination_class = DefaultPagination

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = self.queryset
        user = self.request.user

        if user.role == "admin":
            return queryset.all()

        if user.role == "manager":
            return queryset.filter(
                restaurant=user.restaurant
            )

        return queryset.filter(
            user=user
        )

    def perform_create(self, serializer):
        reservation = serializer.save()
        restaurant_availability_cache.invalidate(restaurant_id=reservation.restaurant_id,date=reservation.start_time.strftime("%Y-%m-%d"),)

    def perform_update(self, serializer):
        reservation = serializer.save()
        restaurant_availability_cache.invalidate(restaurant_id=reservation.restaurant_id,date=reservation.start_time.strftime("%Y-%m-%d"),)

    
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
    permission_classes=[CanCancelReservation],
    )
    def cancel(self, request, pk=None):

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
            ReservationSerializer(reservation).data,
            status=status.HTTP_200_OK,
        )
    

    



