import pytest
from rest_framework import status
from rest_framework.test import APIClient

from decimal import Decimal


from menu.factories import MenuCategoryFactory, MenuItemFactory
from restaurants.factories import RestaurantFactory


@pytest.fixture
def menu_api_client():
    return APIClient()


# menu-category====================================================================

@pytest.mark.django_db
def test_list_menu_categories(menu_api_client):
    MenuCategoryFactory.create_batch(3)

    response = menu_api_client.get("/api/v1/menu-categories/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 3


@pytest.mark.django_db
def test_menu_category_contains_menu_items(menu_api_client):
    category = MenuCategoryFactory()
    MenuItemFactory.create_batch(3, category=category)

    response = menu_api_client.get(f"/api/v1/menu-categories/{category.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["menu_items"]) == 3


@pytest.mark.django_db
def test_menu_category_response_fields(menu_api_client):
    category = MenuCategoryFactory()

    response = menu_api_client.get(f"/api/v1/menu-categories/{category.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data.keys()) == {"id", "name", "restaurant", "menu_items"}


@pytest.mark.django_db
def test_create_menu_category(menu_api_client):
    restaurant = RestaurantFactory()

    response = menu_api_client.post("/api/v1/menu-categories/", {
        "name": "Desserts",
        "restaurant": restaurant.id,
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Desserts"
    assert response.data["restaurant"] == restaurant.id


# menu-items====================================================================

@pytest.mark.django_db
def test_list_menu_items(menu_api_client):
    MenuItemFactory.create_batch(5)

    response = menu_api_client.get("/api/v1/menu-items/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 5


@pytest.mark.django_db
def test_menu_item_response_fields(menu_api_client):
    item = MenuItemFactory()

    response = menu_api_client.get(f"/api/v1/menu-items/{item.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data.keys()) == {"id", "name", "category", "description", "price", "image", "is_available"}


@pytest.mark.django_db
def test_create_menu_item(menu_api_client):
    category = MenuCategoryFactory()

    response = menu_api_client.post("/api/v1/menu-items/", {
        "name": "Tiramisu",
        "category": category.id,
        "description": "Classic Italian dessert",
        "price": "8.50",
        "is_available": True,
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Tiramisu"
    assert response.data["price"] == "8.50"


# filtering ====================================================================

@pytest.mark.django_db
def test_filter_menu_items_by_restaurant(menu_api_client):
    restaurant_a = RestaurantFactory()
    restaurant_b = RestaurantFactory()

    category_a = MenuCategoryFactory(restaurant=restaurant_a)
    category_b = MenuCategoryFactory(restaurant=restaurant_b)

    MenuItemFactory.create_batch(3, category=category_a)
    MenuItemFactory.create_batch(2, category=category_b)

    response = menu_api_client.get("/api/v1/menu-items/", {"restaurant": restaurant_a.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3


@pytest.mark.django_db
def test_filter_menu_items_by_category(menu_api_client):
    category_a = MenuCategoryFactory()
    category_b = MenuCategoryFactory()

    MenuItemFactory.create_batch(4, category=category_a)
    MenuItemFactory.create_batch(2, category=category_b)

    response = menu_api_client.get("/api/v1/menu-items/", {"category": category_a.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 4


@pytest.mark.django_db
def test_filter_menu_items_by_price_range(menu_api_client):
    category = MenuCategoryFactory()
    MenuItemFactory(category=category, price="5.00")
    MenuItemFactory(category=category, price="10.00")
    MenuItemFactory(category=category, price="20.00")

    response = menu_api_client.get("/api/v1/menu-items/", {"price__gte": "8.00", "price__lte": "15.00"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["price"] == "10.00"


@pytest.mark.django_db
def test_filter_menu_items_by_availability(menu_api_client):
    category = MenuCategoryFactory()
    MenuItemFactory.create_batch(3, category=category, is_available=True)
    MenuItemFactory.create_batch(2, category=category, is_available=False)

    response = menu_api_client.get("/api/v1/menu-items/", {"is_available": True})

    assert response.status_code == status.HTTP_200_OK
    assert all(item["is_available"] for item in response.data)


# search====================================================================

@pytest.mark.django_db
def test_search_menu_items_by_name(menu_api_client):
    category = MenuCategoryFactory()
    MenuItemFactory(category=category, name="Margherita Pizza")
    MenuItemFactory(category=category, name="Caesar Salad")

    response = menu_api_client.get("/api/v1/menu-items/", {"search": "Margherita"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Margherita Pizza"


@pytest.mark.django_db
def test_search_menu_items_by_description(menu_api_client):
    category = MenuCategoryFactory()
    MenuItemFactory(category=category, name="Soup", description="Hot tomato bisque")
    MenuItemFactory(category=category, name="Salad", description="Fresh greens")

    response = menu_api_client.get("/api/v1/menu-items/", {"search": "bisque"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Soup"


# ordering====================================================================

@pytest.mark.django_db
def test_order_menu_items_by_price_asc(menu_api_client):
    category = MenuCategoryFactory()
    MenuItemFactory(category=category, name="C item", price="15.00")
    MenuItemFactory(category=category, name="A item", price="5.00")
    MenuItemFactory(category=category, name="B item", price="10.00")

    response = menu_api_client.get("/api/v1/menu-items/", {"ordering": "price"})

    assert response.status_code == status.HTTP_200_OK
    prices = [Decimal(item["price"]) for item in response.data]
    assert prices == sorted(prices)


@pytest.mark.django_db
def test_order_menu_items_by_price_desc(menu_api_client):
    category = MenuCategoryFactory()
    MenuItemFactory(category=category, name="C item", price="15.00")
    MenuItemFactory(category=category, name="A item", price="5.00")
    MenuItemFactory(category=category, name="B item", price="10.00")

    response = menu_api_client.get("/api/v1/menu-items/", {"ordering": "-price"})

    assert response.status_code == status.HTTP_200_OK
    prices = [Decimal(item["price"]) for item in response.data]
    assert prices == sorted(prices, reverse=True)


# restaurant-menu action====================================================================

@pytest.mark.django_db
def test_restaurant_menu_action_returns_categories_with_items(menu_api_client):
    restaurant = RestaurantFactory()
    category = MenuCategoryFactory(restaurant=restaurant)
    MenuItemFactory.create_batch(3, category=category)

    response = menu_api_client.get(f"/api/v1/restaurants/{restaurant.id}/menu/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert len(response.data[0]["menu_items"]) == 3


@pytest.mark.django_db
def test_restaurant_menu_action_returns_only_own_categories(menu_api_client):
    restaurant_a = RestaurantFactory()
    restaurant_b = RestaurantFactory()

    MenuCategoryFactory.create_batch(2, restaurant=restaurant_a)
    MenuCategoryFactory.create_batch(3, restaurant=restaurant_b)

    response = menu_api_client.get(f"/api/v1/restaurants/{restaurant_a.id}/menu/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2