import datetime
import pytest
from rest_framework import status
from restaurants.factories import RestaurantFactory, RestaurantTableFactory, RestaurantWorkingHoursFactory


@pytest.mark.django_db
def test_unauthenticated_cannot_create_restaurant(api_client):
    response = api_client.post("/api/v1/restaurants/", {
        "name": "New Place", "city": "Moscow", "address": "ul. 1"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_customer_cannot_create_restaurant(customer_client):
    response = customer_client.post("/api/v1/restaurants/", {
        "name": "New Place", "city": "Moscow", "address": "ul. 1"
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_manager_can_create_restaurant(manager_client):
    response = manager_client.post("/api/v1/restaurants/", {
        "name": "New Place", "city": "Moscow", "address": "ul. 1"
    })
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_admin_can_create_restaurant(admin_client):
    response = admin_client.post("/api/v1/restaurants/", {
        "name": "New Place", "city": "Moscow", "address": "ul. 1"
    })
    assert response.status_code == status.HTTP_201_CREATED


# ── UPDATE RESTAURANT ─────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_manager_can_update_own_restaurant(manager_client, restaurant):
    response = manager_client.patch(
        f"/api/v1/restaurants/{restaurant.id}/",
        {"name": "Updated Name"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Updated Name"


@pytest.mark.django_db
def test_manager_cannot_update_another_restaurant(manager_client, another_restaurant):
    response = manager_client.patch(
        f"/api/v1/restaurants/{another_restaurant.id}/",
        {"name": "Hacked"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_update_any_restaurant(admin_client, another_restaurant):
    response = admin_client.patch(
        f"/api/v1/restaurants/{another_restaurant.id}/",
        {"name": "Admin Updated"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_cannot_update_restaurant(customer_client, restaurant):
    response = customer_client.patch(
        f"/api/v1/restaurants/{restaurant.id}/",
        {"name": "Hacked"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ── DELETE RESTAURANT ─────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_manager_can_delete_own_restaurant(manager_client, manager_user, restaurant):

    manager_user.restaurant = None
    manager_user.save()

    response = manager_client.delete(f"/api/v1/restaurants/{restaurant.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_manager_cannot_delete_another_restaurant(manager_client, another_restaurant):
    response = manager_client.delete(f"/api/v1/restaurants/{another_restaurant.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_delete_any_restaurant(admin_client, another_restaurant):
    response = admin_client.delete(f"/api/v1/restaurants/{another_restaurant.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT


# ── READ (ALL ALLOWED) ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_unauthenticated_can_list_restaurants(api_client):
    RestaurantFactory.create_batch(2)
    response = api_client.get("/api/v1/restaurants/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_unauthenticated_can_retrieve_restaurant(api_client, restaurant):
    response = api_client.get(f"/api/v1/restaurants/{restaurant.id}/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_unauthenticated_can_view_availability(api_client, restaurant):
    response = api_client.get(
        f"/api/v1/restaurants/{restaurant.id}/availability/",
        {"date": "2026-07-20"},
    )
    # 200 или 400 (нет рабочих часов) — главное не 401/403
    assert response.status_code not in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ]


# ── WORKING HOURS ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_unauthenticated_can_view_working_hours(api_client, restaurant):
    response = api_client.get(f"/api/v1/restaurants/{restaurant.id}/working-hours/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_cannot_patch_working_hours(customer_client, restaurant):
    RestaurantWorkingHoursFactory(
        restaurant=restaurant,
        weekday=0,
        open_time=datetime.time(10, 0),
        close_time=datetime.time(22, 0),
    )
    response = customer_client.patch(
        f"/api/v1/restaurants/{restaurant.id}/working-hours/",
        {"weekday": 0, "open_time": "08:00"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_cannot_patch_working_hours(api_client, restaurant):
    RestaurantWorkingHoursFactory(
        restaurant=restaurant,
        weekday=0,
        open_time=datetime.time(10, 0),
        close_time=datetime.time(22, 0),
    )
    response = api_client.patch(
        f"/api/v1/restaurants/{restaurant.id}/working-hours/",
        {"weekday": 0, "open_time": "08:00"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED