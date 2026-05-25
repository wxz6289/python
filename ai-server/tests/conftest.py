import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
os.environ.setdefault("DEEPSEEK_BASE_URL", "https://api.example.com")


@pytest.fixture
def client():
    from app.main import create_app

    app = create_app(init_master=False, init_db=False)
    with TestClient(app) as test_client:
        yield test_client
