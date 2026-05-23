from app.auth.acl import AuthContext, evaluate_acl_entries, match_conditions
from app.auth.models import AclEffect, AclEntry, SubjectType


def test_match_owner_condition():
    ctx = AuthContext(
        user={"id": 1, "department": "engineering"},
        resource={"owner_id": 1, "id": "session-a"},
    )
    conditions = {
        "all": [{"attr": "resource.owner_id", "op": "eq", "value": "${user.id}"}]
    }
    assert match_conditions(conditions, ctx) is True


def test_deny_overrides_allow():
    entries = [
        AclEntry(
            id=1,
            subject_type=SubjectType.USER,
            subject_id=2,
            resource_type="chat_session",
            resource_id="session-999",
            action="read",
            effect=AclEffect.DENY,
            priority=100,
        )
    ]
    ctx = AuthContext(user={"id": 2}, resource={"id": "session-999", "owner_id": 2})
    assert evaluate_acl_entries(entries, ctx) is False


def test_no_acl_entries_returns_none():
    ctx = AuthContext(user={"id": 1}, resource={"id": "any"})
    assert evaluate_acl_entries([], ctx) is None
