import factory
import random

from .models import Reservation
from restaurants.models import Restaurant

class ReservationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Reservation
    
    guests = factory.Iterator([1, 2, 3, 4, 5, 6])

    status = factory.Iterator([
        "pending",
        "confirmed",
        "completed",
    ])

