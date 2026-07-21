import factory
from django.utils import timezone
from datetime import timedelta

from .models import Reservation

from restaurants.factories import RestaurantFactory, RestaurantTableFactory

class ReservationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Reservation
    
    restaurant = factory.SubFactory(RestaurantFactory)
    table = factory.SubFactory(
        RestaurantTableFactory,
        restaurant=factory.SelfAttribute("..restaurant"),
    )

    start_time = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=1)
    )
    end_time = factory.LazyAttribute(
        lambda obj: obj.start_time + timedelta(hours=2)
    )

    guests = 2

    customer_name = factory.Faker("name")
    customer_phone = "+77001234567"

    status = "pending"

