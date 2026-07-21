import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient


from users.factories import UserFactory
from restaurants.factories import RestaurantFactory
from reservations.factories import ReservationFactory


#get

@pytest.mark.django_db
def test_admin_can_view_all_reservations(
    admin_client,
    restaurant,
    another_restaurant,
    reservations_factory):

    reservations_factory(5, restaurant=restaurant)
    reservations_factory(5, restaurant=another_restaurant)

    response = admin_client.get("/api/v1/reservations/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 10

@pytest.mark.django_db
def test_admin_can_view_any_reservation(admin_client, another_restaurant):
    reservation = ReservationFactory(restaurant=another_restaurant)

    response = admin_client.get(f"/api/v1/reservations/{reservation.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == reservation.id


@pytest.mark.django_db
def test_manager_can_view_only_own_restaurant_reservations(
    manager_client,
    restaurant,
    another_restaurant,
    reservations_factory):

    reservations_factory(5, restaurant=restaurant)
    reservations_factory(5, restaurant=another_restaurant)

    response = manager_client.get("/api/v1/reservations/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5

    for reservation in response.data["results"]:
        assert reservation["restaurant"] == restaurant.id


@pytest.mark.django_db
def test_manager_cannot_view_another_restaurants_reservation(
    manager_client,
    another_restaurant,
):
    reservation = ReservationFactory(restaurant=another_restaurant)

    response = manager_client.get(f"/api/v1/reservations/{reservation.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_non_authenticated_user_cant_view_reservations(
    api_client, 
    restaurant,
    reservations_factory):

    reservations_factory(5, restaurant=restaurant)
    response = api_client.get("/api/v1/reservations/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_customer_can_view_only_own_reservations(
    customer_user,
    customer_client, 
    restaurant,
    another_restaurant,
    reservations_factory,
    another_customer_user):
    

    reservations_factory(5,restaurant=restaurant,user=customer_user)
    reservations_factory(5, restaurant=another_restaurant, user=another_customer_user)

    response = customer_client.get("/api/v1/reservations/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5

    for reservation in response.data["results"]:
        assert reservation["user"] == customer_user.id


@pytest.mark.django_db
def test_customer_cannot_view_another_customers_reservation(
    customer_client,
    another_customer_user,
    restaurant,
):
    reservation = ReservationFactory(restaurant=restaurant, user=another_customer_user)

    response = customer_client.get(f"/api/v1/reservations/{reservation.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND



# reservations status

@pytest.mark.parametrize(
    "action,new_status",
    [
        ("confirm", "confirmed"),
        ("cancel", "canceled"),
        ("complete", "completed"),
    ],
)
@pytest.mark.django_db
def test_manager_can_change_own_restaurant_reservation_status(
    manager_client,
    restaurant,
    reservations_factory,
    action,
    new_status):

    reservation = reservations_factory(
        1,
        restaurant=restaurant,
        status="pending",
    )[0]

    response = manager_client.post(
        f"/api/v1/reservations/{reservation.id}/{action}/"
    )

    assert response.status_code == status.HTTP_200_OK

    reservation.refresh_from_db()

    assert reservation.status == new_status


@pytest.mark.parametrize(
    "action,new_status",
    [
        ("confirm", "confirmed"),
        ("cancel", "canceled"),
        ("complete", "completed"),
    ],
)
@pytest.mark.django_db
def test_manager_cannot_change_another_restaurant_reservation_status(
    manager_client,
    another_restaurant,
    reservations_factory,
    action,
    new_status):

    reservation = reservations_factory(
        1,
        restaurant=another_restaurant,
        status="pending")[0]

    response = manager_client.post(
        f"/api/v1/reservations/{reservation.id}/{action}/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    reservation.refresh_from_db()
    assert reservation.status == "pending"


@pytest.mark.parametrize(
    "action,new_status",
    [
        ("confirm", "confirmed"),
        ("complete", "completed"),
    ],
)
@pytest.mark.django_db
def test_customer_cannot_change_reservation_status(
        customer_client,
        restaurant,
        reservations_factory,
        action,
        new_status
    ):

    reservation = reservations_factory(1,restaurant=restaurant,status="pending")[0]

    response = customer_client.post(
        f"/api/v1/reservations/{reservation.id}/{action}/"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    reservation.refresh_from_db()
    assert reservation.status == "pending"


@pytest.mark.django_db
def test_customer_can_cancel_own_reservation_status(
        customer_client,
        customer_user,
        restaurant,
        reservations_factory,
    ):

    reservation = reservations_factory(
        1,
        restaurant=restaurant,
        status="pending",
        user=customer_user)[0]

    response = customer_client.post(
        f"/api/v1/reservations/{reservation.id}/cancel/"
    )

    assert response.status_code == status.HTTP_200_OK
    reservation.refresh_from_db()
    assert reservation.status == "canceled"


@pytest.mark.django_db
def test_customer_cannot_cancel_another_customers_reservation(
    customer_client,
    another_customer_user,
    restaurant,
):
    reservation = ReservationFactory(
        restaurant=restaurant,
        user=another_customer_user,
        status="pending",
    )

    response = customer_client.post(f"/api/v1/reservations/{reservation.id}/cancel/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    reservation.refresh_from_db()
    assert reservation.status == "pending"


@pytest.mark.parametrize(
    "action,new_status",
    [
        ("confirm", "confirmed"),
        ("cancel", "canceled"),
        ("complete", "completed"),
    ],
)
@pytest.mark.django_db
def test_admin_can_change_any_reservation_status(
    admin_client,
    another_restaurant,
    reservations_factory,
    action,
    new_status,
):
    reservation = reservations_factory(1, restaurant=another_restaurant, status="pending")[0]

    response = admin_client.post(f"/api/v1/reservations/{reservation.id}/{action}/")

    assert response.status_code == status.HTTP_200_OK
    reservation.refresh_from_db()
    assert reservation.status == new_status