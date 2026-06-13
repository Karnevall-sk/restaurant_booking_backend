from collections import defaultdict
from datetime import datetime, time, timedelta
from django.utils import timezone
import random

from restaurants.models import Restaurant
from reservation.factories import ReservationFactory

slots = [
    (12, 14),
    (14, 16),
    (16, 18),
    (18, 20),
    (20, 22),
]

occupied = defaultdict(set)

reservations_count = 300

created = 0
attempts = 0
max_attempts = reservations_count * 10

while created < reservations_count and attempts < max_attempts:
    attempts += 1

    restaurant = random.choice(
        list(Restaurant.objects.all())
    )

    table = random.choice(
        list(restaurant.tables.all())
    )

    day = timezone.now().date() - timedelta(
        days=random.randint(0, 60)
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

    ReservationFactory(
        restaurant=restaurant,
        table=table,
        start_time=start_time,
        end_time=end_time,
    )

    occupied[key].add(slot)
    created += 1