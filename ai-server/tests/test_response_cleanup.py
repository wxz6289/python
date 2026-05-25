from app.middleware.response_cleanup import clean_api_response


def test_clean_api_response_removes_empty_meta():
    payload = {
        "code": 0,
        "msg": "success",
        "data": {"id": 1},
        "meta": {"page": None, "page_size": None, "total": None, "total_pages": None},
    }
    cleaned = clean_api_response(payload)
    assert "meta" not in cleaned


def test_clean_api_response_keeps_pagination_meta():
    payload = {
        "code": 0,
        "msg": "success",
        "data": [],
        "meta": {"page": 1, "page_size": 10, "total": 100, "total_pages": 10},
    }
    cleaned = clean_api_response(payload)
    assert cleaned["meta"]["page"] == 1


def test_clean_api_response_strips_none_from_data():
    payload = {
        "code": 0,
        "msg": "success",
        "data": {"name": "foo", "items": None, "nested": {"a": 1, "b": None}},
    }
    cleaned = clean_api_response(payload)
    assert cleaned["data"] == {"name": "foo", "nested": {"a": 1}}


def test_clean_api_response_keeps_top_level_null_data():
    payload = {"code": 422, "msg": "error", "data": None}
    cleaned = clean_api_response(payload)
    assert cleaned["data"] is None
