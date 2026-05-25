from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SubjectType(str, Enum):
    USER = "user"
    ROLE = "role"


class AclEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class AuthContext:
    user: dict[str, Any]
    resource: dict[str, Any] = field(default_factory=dict)
    env: dict[str, Any] = field(default_factory=dict)
