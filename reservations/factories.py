import factory

from .models import Reservation

class ReservationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Reservation
    
    guests = factory.Iterator([1, 2, 3, 4, 5, 6])

    customer_name = factory.Faker("name")
    customer_phone = "+77001234567"

    status = factory.Iterator([
        "pending",
        "confirmed",
        "canceled",
    ])

