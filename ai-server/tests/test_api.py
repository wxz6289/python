def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_item(client):
    response = client.post(
        "/items",
        json={"name": "foo", "description": "bar", "price": 9.9},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "foo"


def test_create_item_validation_error(client):
    response = client.post(
        "/items",
        json={"name": "foo", "description": "bar", "price": -1},
    )
    assert response.status_code == 422
