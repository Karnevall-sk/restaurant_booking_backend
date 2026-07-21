import datetime
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from restaurants.factories import (
    RestaurantFactory,
    RestaurantTableFactory,
    RestaurantWorkingHoursFactory,
    RestaurantClosureFactory,
)


# ── RESTAURANT CRUD ───────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_restaurants(api_client):
    RestaurantFactory.create_batch(3)
    response = api_client.get("/api/v1/restaurants/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 3


@pytest.mark.django_db
def test_retrieve_restaurant(api_client):
    restaurant = RestaurantFactory()
    response = api_client.get(f"/api/v1/restaurants/{restaurant.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == restaurant.id
    assert set(response.data.keys()) == {
        "id", "name", "city", "address", "description",
        "reservation_duration", "created_at", "is_active",
    }


@pytest.mark.django_db
def test_create_restaurant(admin_client):
    response = admin_client.post("/api/v1/restaurants/", {
        "name": "Test Restaurant",
        "city": "Almaty",
        "address": "ul. Lenina 1",
        "reservation_duration": 90,
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test Restaurant"
    assert response.data["reservation_duration"] == 90


@pytest.mark.django_db
def test_search_restaurants_by_name(api_client):
    RestaurantFactory(name="Unique Sushi Place")
    RestaurantFactory(name="Random Burger Joint")
    response = api_client.get("/api/v1/restaurants/", {"search": "Sushi"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Unique Sushi Place"


@pytest.mark.django_db
def test_filter_restaurants_by_city(api_client):
    RestaurantFactory.create_batch(3, city="Almaty")
    RestaurantFactory.create_batch(2, city="SPb")
    response = api_client.get("/api/v1/restaurants/", {"city": "Almaty"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    for r in response.data:
        assert r["city"] == "Almaty"    


# ── TABLES ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_tables(api_client):
    RestaurantTableFactory.create_batch(4)
    response = api_client.get("/api/v1/tables/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 4


@pytest.mark.django_db
def test_create_table(admin_client):
    restaurant = RestaurantFactory()
    response = admin_client.post("/api/v1/tables/", {
        "restaurant": restaurant.id,
        "name": "VIP Table",
        "seats": 6,
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "VIP Table"
    assert response.data["seats"] == 6


@pytest.mark.django_db
def test_table_name_unique_per_restaurant(admin_client):
    restaurant = RestaurantFactory()
    RestaurantTableFactory(restaurant=restaurant, name="Table 1")

    response = admin_client.post("/api/v1/tables/", {
        "restaurant": restaurant.id,
        "name": "Table 1",
        "seats": 4,
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── MENU ACTION ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_restaurant_menu_returns_only_own_categories(api_client):
    from menu.factories import MenuCategoryFactory, MenuItemFactory

    restaurant_a = RestaurantFactory()
    restaurant_b = RestaurantFactory()
    cat_a = MenuCategoryFactory(restaurant=restaurant_a)
    MenuCategoryFactory(restaurant=restaurant_b)
    MenuItemFactory.create_batch(2, category=cat_a)

    response = api_client.get(f"/api/v1/restaurants/{restaurant_a.id}/menu/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert len(response.data[0]["menu_items"]) == 2


# ── AVAILABILITY ACTION ───────────────────────────────────────────────────────

@pytest.mark.django_db
def test_availability_requires_date_param(api_client):
    restaurant = RestaurantFactory()
    response = api_client.get(f"/api/v1/restaurants/{restaurant.id}/availability/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_availability_invalid_date_returns_400(api_client):
    restaurant = RestaurantFactory()
    response = api_client.get(
        f"/api/v1/restaurants/{restaurant.id}/availability/",
        {"date": "not-a-date"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_availability_returns_slots_on_working_day(api_client):
    restaurant = RestaurantFactory()
    RestaurantTableFactory(restaurant=restaurant, seats=4)

    target_date = datetime.date(2026, 7, 20)  # понедельник
    RestaurantWorkingHoursFactory(
        restaurant=restaurant,
        weekday=target_date.weekday(),
        open_time=datetime.time(10, 0),
        close_time=datetime.time(22, 0),
    )

    response = api_client.get(
        f"/api/v1/restaurants/{restaurant.id}/availability/",
        {"date": target_date.isoformat()},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_closed"] is False
    assert response.data["closure_reason"] is None
    assert len(response.data["slots"]) > 0
    assert "time" in response.data["slots"][0]
    assert "available" in response.data["slots"][0]


@pytest.mark.django_db
def test_availability_day_off_returns_empty_slots(api_client):
    restaurant = RestaurantFactory()
    target_date = datetime.date(2026, 7, 20)
    RestaurantWorkingHoursFactory(
        restaurant=restaurant,
        weekday=target_date.weekday(),
        is_day_off=True,
        open_time=None,
        close_time=None,
    )

    response = api_client.get(
        f"/api/v1/restaurants/{restaurant.id}/availability/",
        {"date": target_date.isoformat()},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["slots"] == []


@pytest.mark.django_db
def test_availability_closure_returns_is_closed(api_client):
    restaurant = RestaurantFactory()
    target_date = datetime.date(2026, 7, 20)
    RestaurantClosureFactory(
        restaurant=restaurant,
        date=target_date,
        reason="Renovation",
    )

    response = api_client.get(
        f"/api/v1/restaurants/{restaurant.id}/availability/",
        {"date": target_date.isoformat()},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_closed"] is True
    assert response.data["closure_reason"] == "Renovation"
    assert response.data["slots"] == []


# ── WORKING HOURS ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_manager_can_get_working_hours(manager_client, restaurant):
    RestaurantWorkingHoursFactory.create_batch(3, restaurant=restaurant)
    response = manager_client.get(f"/api/v1/restaurants/{restaurant.id}/working-hours/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3


@pytest.mark.django_db
def test_manager_can_patch_working_hours(manager_client, restaurant):
    RestaurantWorkingHoursFactory(
        restaurant=restaurant,
        weekday=0,
        open_time=datetime.time(10, 0),
        close_time=datetime.time(22, 0),
    )
    response = manager_client.patch(
        f"/api/v1/restaurants/{restaurant.id}/working-hours/",
        {"weekday": 0, "open_time": "09:00", "close_time": "23:00"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["open_time"] == "09:00:00"
    assert response.data["close_time"] == "23:00:00"


@pytest.mark.django_db
def test_unauthenticated_can_get_working_hours(api_client):
    restaurant = RestaurantFactory()
    response = api_client.get(f"/api/v1/restaurants/{restaurant.id}/working-hours/")
    assert response.status_code == status.HTTP_200_OK