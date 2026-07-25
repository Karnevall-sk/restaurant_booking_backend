from django.core.cache import cache
import pytest

@pytest.mark.django_db
def test_create_restaurant_invalidates_cache(admin_client):

    cache.set("restaurants:list", {"test": True})

    assert cache.get("restaurants:list") is not None

    response = admin_client.post(
        "/api/v1/restaurants/",
        {
            "name": "Restaurant",
            "city": "Astana",
            "address": "Street",
            "description": "Test",
        },
    )

    assert response.status_code == 201

    assert cache.get("restaurants:list") is None


@pytest.mark.django_db
def test_update_restaurant_invalidates_cache(
    admin_client,
    restaurant,
):

    cache.set("restaurants:list", {"test": True})

    response = admin_client.patch(
        f"/api/v1/restaurants/{restaurant.id}/",
        {
            "name": "New name",
        },
    )

    assert response.status_code == 200

    assert cache.get("restaurants:list") is None


@pytest.mark.django_db
def test_delete_restaurant_invalidates_cache(
    admin_client,
    restaurant,
):

    cache.set("restaurants:list", {"test": True})

    response = admin_client.delete(
        f"/api/v1/restaurants/{restaurant.id}/"
    )

    assert response.status_code == 204

    assert cache.get("restaurants:list") is None