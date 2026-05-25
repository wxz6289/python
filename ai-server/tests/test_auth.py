import pytest

from app.auth.domain.value_objects import AuthContext
from app.auth.domain.services import match_conditions
from app.auth.infrastructure.security import hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_abac_department_rule():
    ctx = AuthContext(
        user={"department": "finance"},
        resource={"department": "finance"},
    )
    conditions = {
        "all": [
            {
                "attr": "user.department",
                "op": "eq",
                "value": "${resource.department}",
            }
        ]
    }
    assert match_conditions(conditions, ctx) is True


@pytest.mark.asyncio
async def test_compose_mysql_config_matches_compose_file():
    from app.infra.compose import get_mysql_compose_config

    mysql = get_mysql_compose_config()
    assert mysql["port"] == 3309
    assert mysql["password"] == "ai-server123"
    assert mysql["database"] == "ai_server"


@pytest.mark.asyncio
async def test_prepare_chat_access_denied_without_token(client):
    response = client.get("/chat", params={"query": "hello"})
    assert response.status_code == 401
    body = response.json()
    assert body["code"] == 401
    assert body["data"] is None
    assert "meta" not in body
