from collections import defaultdict
from datetime import datetime, time, timedelta
from django.utils import timezone
import random
from django.db import IntegrityError

from restaurants.models import Restaurant
from reservations.factories import ReservationFactory

def seed_reservations(reservations_count = 300):

    slots = [
        (10,12),
        (12, 14),
        (14, 16),
        (16, 18),
        (18, 20),

    ]

    occupied = defaultdict(set)

    created = 0
    attempts = 0
    max_attempts = reservations_count * 10

    restaurants = list(Restaurant.objects.all())
    tables_by_restaurant = {
        restaurant.id: list(restaurant.tables.all()) for restaurant in restaurants
    }

    while created < reservations_count and attempts < max_attempts:
        attempts += 1

        restaurant = random.choice(restaurants)

        table = random.choice(tables_by_restaurant[restaurant.id])

        day = timezone.now().date() - timedelta(
            days=random.randint(0, 10)
        )

        slot = random.choice(slots)

        key = (table.id, day)

        if slot in occupied[key]:
            continue

        start_hour, end_hour = slot

        start_time = timezone.make_aware(
            datetime.combine(day, time(start_hour))
        )

        end_time = timezone.make_aware(
            datetime.combine(day, time(end_hour))
        )

        try:
            ReservationFactory(
                restaurant=restaurant,
                table=table,
                start_time=start_time,
                end_time=end_time,
            )
        except IntegrityError:
            continue

        occupied[key].add(slot)
        created += 1