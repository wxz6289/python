def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["msg"] == "success"
    assert body["data"] == {"status": "ok"}
    assert "meta" not in body


def test_create_item(client):
    response = client.post(
        "/items",
        json={"name": "foo", "description": "bar", "price": 9.9},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["name"] == "foo"
    assert "meta" not in body


def test_get_items_pagination_meta(client):
    response = client.get("/items/v1", params={"page": 2, "page_size": 10})
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert len(body["data"]) == 10
    assert body["meta"] == {
        "page": 2,
        "page_size": 10,
        "total": 100,
        "total_pages": 10,
    }


def test_create_item_validation_error(client):
    response = client.post(
        "/items",
        json={"name": "foo", "description": "bar", "price": -1},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == 422
    assert "price" in body["msg"]
    assert body["data"] is None


def test_path_page2_validation_error(client):
    response = client.get("/path/page2/12")
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == 422
    assert body["msg"] == "page: Invalid page pattern 12"
    assert body["data"] is None


def test_response_strips_none_fields_from_data(client):
    response = client.get("/items/v2/1")
    assert response.status_code == 200
    body = response.json()
    assert "q" not in body["data"]
    assert body["data"]["item"]["name"] == "Item 1"


def test_response_strips_unset_optional_fields(client):
    response = client.get("/items/query7/q", params={"q": "test"})
    assert response.status_code == 200
    body = response.json()
    assert "items" not in body["data"]
    assert body["data"]["name"] == "test"

