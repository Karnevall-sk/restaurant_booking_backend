from django.shortcuts import render

from .serializers import UserSerializer, MeSerializer, UpdateMeSerializer

from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated

from reservations.models import Reservation
from reservations.serializers import ReservationSerializer


class UserViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    @action(
        detail=False,
        methods=["GET", "PATCH"],
        url_path="me"
    )
    def user_info(self, request):

        if request.method == "GET":
            serializer = MeSerializer(request.user)
            return Response(serializer.data)

        serializer = UpdateMeSerializer(
        request.user,
        data=request.data,
        partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(MeSerializer(request.user).data)


class UserReservationsViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer
    def get_queryset(self):
            
        return  Reservation.objects.filter(
            user = self.request.user
        )
        