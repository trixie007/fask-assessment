import pytest
from unittest.mock import patch, Mock
from argparse import Namespace

import app as app_module
from app import app, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

# Clear inventory before each test
@pytest.fixture(autouse=True)
def clear_inventory():
    inventory.clear()
    app_module.next_id = 1


#api tests

def test_get_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200
    assert response.get_json() == []


@patch("app.fetch_product")
def test_post_inventory(mock_fetch_product, client):
    mock_fetch_product.return_value = {
        "name": "Nutella",
        "barcode": "3017620422003",
        "brand": "Nutella, Ferrero",
        "category": "Chocolate spread",
        "ingredients": "Sugar, hazelnuts, cocoa",
        "image": "https://example.com/nutella.jpg"
    }

    response = client.post(
        "/inventory",
        json={
            "name": "Nutella",
            "quantity": 5,
            "price": 500,
            "barcode": "3017620422003"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 1
    assert data["name"] == "Nutella"
    assert data["quantity"] == 5
    assert data["price"] == 500
    assert data["brand"] == "Nutella, Ferrero"

    mock_fetch_product.assert_called_once_with(
        barcode="3017620422003"
    )


@patch("app.fetch_product")
def test_get_single_inventory_item(mock_fetch_product, client):
    mock_fetch_product.return_value = {
        "name": "Milk",
        "barcode": "123456789",
        "brand": "Test Brand",
        "category": "Dairy",
        "ingredients": "Milk",
        "image": "https://example.com/milk.jpg"
    }

    client.post(
        "/inventory",
        json={
            "name": "Milk",
            "quantity": 10,
            "price": 150,
            "barcode": "123456789"
        }
    )

    response = client.get("/inventory/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == 1
    assert data["name"] == "Milk"
    assert data["quantity"] == 10
    assert data["price"] == 150


@patch("app.fetch_product")
def test_patch_inventory_item(mock_fetch_product, client):
    mock_fetch_product.return_value = {
        "name": "Milk",
        "barcode": "123456789",
        "brand": "Test Brand",
        "category": "Dairy",
        "ingredients": "Milk",
        "image": "https://example.com/milk.jpg"
    }

    client.post(
        "/inventory",
        json={
            "name": "Milk",
            "quantity": 10,
            "price": 150,
            "barcode": "123456789"
        }
    )

    response = client.patch(
        "/inventory/1",
        json={
            "quantity": 20,
            "price": 200
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["quantity"] == 20
    assert data["price"] == 200


@patch("app.fetch_product")
def test_delete_inventory_item(mock_fetch_product, client):
    mock_fetch_product.return_value = {
        "name": "Milk",
        "barcode": "123456789",
        "brand": "Test Brand",
        "category": "Dairy",
        "ingredients": "Milk",
        "image": "https://example.com/milk.jpg"
    }

    client.post(
        "/inventory",
        json={
            "name": "Milk",
            "quantity": 10,
            "price": 150,
            "barcode": "123456789"
        }
    )

    response = client.delete("/inventory/1")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Item deleted"

    response = client.get("/inventory")

    assert response.get_json() == []



# ERROR TESTS


def test_get_missing_item(client):
    response = client.get("/inventory/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found"


def test_post_missing_price(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Milk",
            "quantity": 10
        }
    )

    assert response.status_code == 400
    assert "price is required" in response.get_json()["error"]


def test_invalid_quantity(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Milk",
            "quantity": -5,
            "price": 150
        }
    )

    assert response.status_code == 400


# external api tests

@patch("external_api.requests.get")
def test_fetch_product_by_barcode(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200

    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Nutella",
            "code": "3017620422003",
            "brands": "Nutella, Ferrero",
            "categories": "Chocolate spread",
            "ingredients_text": "Sugar, hazelnuts, cocoa",
            "image_url": "https://example.com/nutella.jpg"
        }
    }

    mock_get.return_value = mock_response

    from external_api import fetch_product

    result = fetch_product(
        barcode="3017620422003"
    )

    assert result["name"] == "Nutella"
    assert result["barcode"] == "3017620422003"

    mock_get.assert_called_once()


@patch("external_api.requests.get")
def test_fetch_product_by_name(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200

    mock_response.json.return_value = {
        "products": [
            {
                "product_name": "Nutella",
                "code": "3017620422003",
                "brands": "Nutella, Ferrero",
                "categories": "Chocolate spread",
                "ingredients_text": "Sugar, hazelnuts, cocoa",
                "image_url": "https://example.com/nutella.jpg"
            }
        ]
    }

    mock_get.return_value = mock_response

    from external_api import fetch_product

    result = fetch_product(
        name="nutella"
    )

    assert result["name"] == "Nutella"
    assert result["barcode"] == "3017620422003"

    mock_get.assert_called_once()


@patch("external_api.requests.get")
def test_external_api_product_not_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200

    mock_response.json.return_value = {
        "status": 0
    }

    mock_get.return_value = mock_response

    from external_api import fetch_product

    result = fetch_product(
        barcode="0000000000000"
    )

    assert result is None


# lookup
@patch("app.fetch_product")
def test_lookup_by_barcode(mock_fetch_product, client):
    mock_fetch_product.return_value = {
        "name": "Nutella",
        "barcode": "3017620422003",
        "brand": "Nutella, Ferrero",
        "category": "Chocolate spread",
        "ingredients": "Sugar",
        "image": "https://example.com/nutella.jpg"
    }

    response = client.get(
        "/lookup?barcode=3017620422003"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["name"] == "Nutella"
    assert data["barcode"] == "3017620422003"


def test_lookup_without_search_parameter(client):
    response = client.get("/lookup")

    assert response.status_code == 400
    assert "barcode or product name" in response.get_json()["error"]


# cli tests


# CLI tests

def test_cli_add_item(capsys, monkeypatch):
    from cli import add_item

    response = Mock()
    response.status_code = 201
    response.json.return_value = {
        "id": 1,
        "name": "Milk",
        "quantity": 10,
        "price": 150
    }

    answers = iter(["Milk", "10", "150", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    with patch("cli.requests.post", return_value=response):
        add_item()

    output = capsys.readouterr().out
    assert "Item added successfully" in output


def test_cli_list_items(capsys):
    from cli import list_items

    response = Mock()
    response.status_code = 200
    response.json.return_value = [
        {
            "id": 1,
            "name": "Milk",
            "quantity": 10,
            "price": 150
        }
    ]

    with patch("cli.requests.get", return_value=response):
        list_items()

    output = capsys.readouterr().out
    assert "Milk" in output
    assert "Quantity: 10" in output



def test_cli_update_item(capsys, monkeypatch):
    from cli import update_item

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "id": 1,
        "name": "Milk",
        "quantity": 20,
        "price": 200
    }

    # Item ID, update choice (3 = both), price, quantity
    answers = iter(["1", "3", "200", "20"])
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    with patch("cli.requests.patch", return_value=response):
        update_item()

    output = capsys.readouterr().out
    assert "Item updated successfully" in output




def test_cli_delete_item(capsys, monkeypatch):
    from cli import delete_item

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "message": "Item deleted"
    }

    # Enter the item ID, then type "yes" to confirm.
    answers = iter(["1", "yes"])
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    with patch("cli.requests.delete", return_value=response):
        delete_item()

    output = capsys.readouterr().out
    assert "Delete request completed." in output
    assert "Item deleted" in output



