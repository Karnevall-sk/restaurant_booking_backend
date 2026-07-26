from django.core.cache import cache
import pytest
from restaurants.cache import restaurant_menu_cache, restaurant_list_cache
from menu.factories import MenuCategoryFactory, MenuItemFactory


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


 # MENU----------------------------------------------


@pytest.mark.django_db
def test_restaurant_menu_is_cached(api_client, restaurant):

    cache.clear()

    response = api_client.get(
        f"/api/v1/restaurants/{restaurant.id}/menu/"
    )

    assert response.status_code == 200

    key = restaurant_menu_cache._make_key(
        restaurant_id=restaurant.id
    )

    assert cache.get(key) == response.data

@pytest.mark.django_db
def test_menu_item_update_invalidates_menu_cache(
    admin_client,
    restaurant,
):

    category = MenuCategoryFactory(
        restaurant=restaurant
    )

    item = MenuItemFactory(
        category=category
    )

    key = restaurant_menu_cache._make_key(
        restaurant_id=restaurant.id
    )

    cache.set(key, {"cached": True})

    assert cache.get(key) is not None

    response = admin_client.patch(
        f"/api/v1/menu-items/{item.id}/",
        {
            "price": 999
        },
        format="json",
    )

    assert response.status_code == 200

    assert cache.get(key) is None