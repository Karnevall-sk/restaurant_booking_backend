from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
import pytest

from restaurants.factories import RestaurantFactory, RestaurantTableFactory
from reservations.factories import ReservationFactory
from reservations.models import Reservation

from reservations.services import calculate_end_time, find_available_table, create_reservation



# Tests for test_find_available_table

@pytest.mark.django_db
def test_find_available_table():

    restaurant = RestaurantFactory()

    RestaurantTableFactory(
        restaurant=restaurant,
        seats=2,
    )

    expected_table = RestaurantTableFactory(
        restaurant=restaurant,
        seats=4,
    )

    RestaurantTableFactory(
        restaurant=restaurant,
        seats=6,
    )

    table = find_available_table(
        restaurant=restaurant,
        start_time=timezone.make_aware(
            datetime(2026, 7, 15, 14, 0)
        ),
        guests=3,
    )

    assert table == expected_table



@pytest.mark.django_db
def test_find_available_table_no_suitable_table():

    restaurant = RestaurantFactory()

    RestaurantTableFactory(
        restaurant=restaurant,
        seats=2,
    )

    RestaurantTableFactory(
        restaurant=restaurant,
        seats=4,
    )

    with pytest.raises(ValidationError) as exc_info:
        find_available_table(
            restaurant=restaurant,
            start_time=timezone.make_aware(
                datetime(2026, 7, 15, 14, 0)
            ),
            guests=6,
        )
    
    

    assert exc_info.value.detail["table"] == "No available table for the selected time."

@pytest.mark.django_db
def test_find_available_table_ignores_reserved_tables():

    restaurant = RestaurantFactory()
    reserved_table = RestaurantTableFactory(
        restaurant=restaurant, 
        seats=6
        )
    start = timezone.now()
    end = start + timedelta(hours=2)

    ReservationFactory(
        restaurant=restaurant,
        table=reserved_table,
        start_time=start,
        end_time=end
    )

    free_table = RestaurantTableFactory(
        restaurant=restaurant, 
        seats=6
        )
    start = timezone.now()


    table = find_available_table(
        restaurant=restaurant,
        start_time=start,
        guests=6,
        )
    
    assert table == free_table



class FakeRestaurant:
    reservation_duration = 120


def test_calculate_end_time():

    restaurant = FakeRestaurant()

    start_time = datetime(
        2026,
        7,
        15,
        14,
        0,
    )

    end_time = calculate_end_time(
        restaurant=restaurant,
        start_time=start_time,
    )

    
    assert end_time == start_time + timedelta(minutes=120)




# Tests for create_reservation

@pytest.mark.django_db
def test_create_reservation_success_auto_table():

    restaurant = RestaurantFactory()

    table = RestaurantTableFactory(restaurant=restaurant, seats=4)
    
    start_time = timezone.now() + timedelta(days=1)
    
    data = {
        "restaurant": restaurant,
        "start_time": start_time,
        "guests": 4,
        "status": "pending", 
    }

    initial_count = Reservation.objects.count()

    reservation = create_reservation(**data)

    assert isinstance(reservation, Reservation)
    
    # reservation added
    assert Reservation.objects.count() == initial_count + 1
    
    # all data is correct
    assert reservation.restaurant == restaurant
    assert reservation.table == table  
    assert reservation.start_time == start_time
    assert reservation.guests == 4

@pytest.mark.django_db
def test_create_reservation_table_already_reserved():
    
    restaurant = RestaurantFactory()
    table = RestaurantTableFactory(restaurant=restaurant, seats=4)
    start_time = timezone.now()
    end_time = start_time + timedelta(minutes=120)
    
    ReservationFactory(
        restaurant=restaurant,
        table=table,
        start_time=start_time,
        end_time=end_time,
    )


    #creating another reservation
    with pytest.raises(ValidationError) as exc_info: 
        create_reservation(
            restaurant=restaurant,
            table=table,   
            start_time=start_time,
            guests=4,
        )

    assert "Table already reserved." in str(exc_info.value)


@pytest.mark.django_db
def test_create_reservation_table_not_belong_to_restaurant():

    restaurant_a = RestaurantFactory()
    restaurant_b = RestaurantFactory()
    table = RestaurantTableFactory(restaurant=restaurant_a, seats = 2)
    start_time = timezone.now()

    with pytest.raises(ValidationError) as exc_info:
        create_reservation(
            restaurant=restaurant_b,
            table=table,
            start_time=start_time,
            guests=2
        )
    assert "Table does not belong to restaurant." in str(exc_info.value)
