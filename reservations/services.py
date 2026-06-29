from datetime import date, datetime, timedelta
import zoneinfo

from .models import Reservation
from restaurants.models import Restaurant, RestaurantWorkingHours



SLOT_INTERVAL_MINUTES = 30

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

    #

    # for slot_start in slots:
    #     slots_end = slot_start + duration

    #     reservations_for_slot = set()
    #     slot_reservations_dict = {}

    #     time_key = slot_start.strftime("%H:%M")

    #     for i in active_reservations:
    #         if i.start_time < slots_end and i.end_time > slot_start:
                
    #             table_id = i.table.id if hasattr(i.table, 'id') else i.table
    #             reservations_for_slot.add(table_id)

    #             table_status = {}
    #             table_status[table_id] = f"{i.status} {i.start_time.strftime("%H:%M")}"
                
    #             if time_key not in slot_reservations_dict:
    #                 slot_reservations_dict[time_key] = []
                
    #             slot_reservations_dict[time_key].append(table_status)
    #     result.append({
    #         "time": slot_start.strftime("%H:%M"),
    #         "available": len(reservations_for_slot) < table_count,
    #         "reservations": slot_reservations_dict
    #     })
    # print(reservations_for_slot)
    # return result
    




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
