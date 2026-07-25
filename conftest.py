import pytest
from rest_framework.test import APIClient
from django.core.cache import cache

from restaurants.factories import RestaurantFactory
from reservations.factories import ReservationFactory
from users.factories import UserFactory


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

# api client
@pytest.fixture
def api_client():
    return APIClient()


# Users fixture

@pytest.fixture
def admin_user():
    return UserFactory(
        role="admin",
        is_staff=True,
        is_superuser=True,
    )



@pytest.fixture
def manager_user(restaurant):
    return UserFactory(
        role="manager",
        restaurant=restaurant,
    )


@pytest.fixture
def customer_user():
    return UserFactory(role="customer")

@pytest.fixture
def another_customer_user():
    return UserFactory(role="customer")


# clients fixtures

@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(admin_user)
    return client


@pytest.fixture
def manager_client(api_client, manager_user):
    api_client.force_authenticate(user=manager_user)
    return api_client


@pytest.fixture
def customer_client(api_client, customer_user):
    api_client.force_authenticate(user=customer_user)
    return api_client



@pytest.fixture
def restaurant():
    return RestaurantFactory()

@pytest.fixture
def another_restaurant():
    return RestaurantFactory()


@pytest.fixture
def reservation(restaurant):
    return ReservationFactory(restaurant=restaurant)

@pytest.fixture
def reservations_factory():
    def create(count=1, **kwargs):
        return ReservationFactory.create_batch(count, **kwargs)
    return create