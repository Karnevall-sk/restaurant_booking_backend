from datetime import date, datetime, timedelta
import zoneinfo

from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .models import Reservation
from restaurants.models import Restaurant, RestaurantWorkingHours, RestaurantTable



SLOT_INTERVAL_MINUTES = 30


def create_reservation(**data):
    restaurant = data["restaurant"]
    if data["table"]:
        table = data["table"]
    else:
        table = find_available_table()

    if table.restaurant_id != restaurant.id:
        raise ValidationError(
            "Table does not belong to restaurant."
        )

    end_time = calculate_end_time(
        restaurant=restaurant,
        start_time=data["start_time"],
    )

    check_table_availability(
        table=table,
        start_time=data["start_time"],
        end_time=end_time,
    )
    
    data["end_time"] = end_time

    try:
        return Reservation.objects.create(**data)

    except IntegrityError as e:
        if "no_overlapping_reservations" in str(e):
            raise ValidationError({
                "table": "Table is already reserved."
            })

        raise

def confirm_reservation(
        reservation: Reservation
):
    if reservation.status == "Canceled":
        raise ValidationError("Reservations was canceled")
    reservation.status = "Confirm"
    reservation.save(update_fields=["status"])

def cancel_reservation(
        reservation: Reservation
):
    if reservation.status == "Canceled":
        raise ValidationError("Already canceled")
    if reservation.status == "Completed":
        raise ValidationError("Completed reservation cannot be cancelled")
    reservation.status = "Canceled"
    reservation.save(update_fields=["status"])


def complete_reservation(
        reservation: Reservation
):
    if reservation.status == "Canceled":
        raise ValidationError("Canceled reservation cannot be cancelled")
    if reservation.status == "Completed":
        raise ValidationError("Already completed")
    reservation.status = "Completed"
    reservation.save(update_fields=["status"])




def find_available_table(
        restaurant: Restaurant,
        start_time: date,
        guests: int,
    ):
    end_time = calculate_end_time(restaurant, start_time)

    table = RestaurantTable.objects.filter(
        restaurant = restaurant,
        seats__gte=guests,
    ).exclude(
        reservations__status__in =["pending", "confirmed"],
        reservations__start_time__lt = end_time,
        reservations__end_time__gt = start_time,
    ).order_by("seats").first()

    if table is None:
        raise ValidationError(
            "No available table for selected time."
        )

    return table

def check_table_availability(
    table,
    start_time,
    end_time):

    exists = Reservation.objects.filter(
        table=table,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exists()

    if exists:
        raise ValidationError(
            "Table already reserved"
        )

def get_slots_for_date(restaurant: Restaurant, target_date: date) -> list[dict]:

    table_count = restaurant.tables.count()
    if table_count == 0:
        return []
    
    weekday = target_date.weekday()

    try:
        working_hours = restaurant.working_hours.get(weekday=weekday)
    except RestaurantWorkingHours.DoesNotExist:
        return []

    if working_hours.is_day_off:
        return []

    tz = zoneinfo.ZoneInfo("UTC")
    day_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=tz)
    day_end = day_start + timedelta(days=1)

    active_reservations = Reservation.objects.filter(
        restaurant = restaurant,
        status__in = ["pending", "confirmed"],
        start_time__lt = day_end,
        end_time__gt = day_start
    ).select_related("table")

    duration = timedelta(minutes=restaurant.reservation_duration)
    slots = _generate_slots(target_date, working_hours, duration, tz)
    if not slots:
        return []

    result = []

    for slot_start in slots:
        slots_end = slot_start + duration
        reservations_for_slot = set()

        for i in active_reservations:
            if i.start_time < slots_end and i.end_time > slot_start:
                table_id = i.table.id if hasattr(i.table, 'id') else i.table
                reservations_for_slot.add(table_id)

        result.append({
            "time": slot_start.strftime("%H:%M"),
            "available": len(reservations_for_slot) < table_count
        })

    return result



def _generate_slots(
    target_date: date,
    working_hours: RestaurantWorkingHours,
    duration: timedelta,
    tz,
) -> list[datetime]:

    open_dt = datetime.combine(target_date, working_hours.open_time).replace(tzinfo=tz)

    if working_hours.closes_next_day:
        next_day = target_date + timedelta(days=1)
        close_dt = datetime.combine(next_day, working_hours.close_time).replace(tzinfo=tz)
    else:
        close_dt = datetime.combine(target_date, working_hours.close_time).replace(tzinfo=tz)

    last_slot_start = close_dt - duration

    slots = []
    current = open_dt

    interval = timedelta(minutes=SLOT_INTERVAL_MINUTES)

    while current <= last_slot_start:
        slots.append(current)
        current += interval

    return slots


def calculate_end_time(
    restaurant: Restaurant,
    start_time: datetime,
    ) -> datetime:
    return start_time + timedelta(
        minutes=restaurant.reservation_duration
    )
