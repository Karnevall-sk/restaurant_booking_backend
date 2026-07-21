import pytest
from rest_framework.test import APIClient

from restaurants.factories import RestaurantFactory
from reservations.factories import ReservationFactory
from users.factories import UserFactory


# restaurants fixtures

@pytest.fixture
def restaurant():
    return RestaurantFactory()


@pytest.fixture
def another_restaurant():
    return RestaurantFactory()


# reservation fixtures

@pytest.fixture
def reservation(restaurant):
    return ReservationFactory(
        restaurant=restaurant
    )

@pytest.fixture
def reservations_factory():

    def create(count=1, **kwargs):
        return ReservationFactory.create_batch(
            count,
            **kwargs,
        )

    return create