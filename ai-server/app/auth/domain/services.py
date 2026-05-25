from __future__ import annotations

from typing import Any, Protocol

from app.auth.domain.value_objects import AuthContext, AclEffect


class AclEntryLike(Protocol):
    effect: AclEffect
    conditions: dict[str, Any] | None


def _resolve_attr(path: str, ctx: AuthContext) -> Any:
    root_name, _, remainder = path.partition(".")
    if root_name == "user":
        current: Any = ctx.user
    elif root_name == "resource":
        current = ctx.resource
    elif root_name == "env":
        current = ctx.env
    else:
        return None

    if not remainder:
        return current

    for part in remainder.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _resolve_value(value: Any, ctx: AuthContext) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        return _resolve_attr(value[2:-1], ctx)
    return value


def _compare(left: Any, operator: str, right: Any) -> bool:
    if operator == "eq":
        return left == right
    if operator == "ne":
        return left != right
    if operator == "in":
        return left in (right if isinstance(right, (list, tuple, set)) else [right])
    if operator == "between":
        if not isinstance(right, (list, tuple)) or len(right) != 2:
            return False
        return right[0] <= left <= right[1]
    return False


def match_conditions(conditions: dict[str, Any] | None, ctx: AuthContext) -> bool:
    if not conditions:
        return True

    all_rules = conditions.get("all")
    if isinstance(all_rules, list):
        return all(
            _compare(
                _resolve_attr(rule["attr"], ctx),
                rule["op"],
                _resolve_value(rule.get("value"), ctx),
            )
            for rule in all_rules
            if isinstance(rule, dict) and "attr" in rule and "op" in rule
        )

    any_rules = conditions.get("any")
    if isinstance(any_rules, list) and any_rules:
        return any(
            _compare(
                _resolve_attr(rule["attr"], ctx),
                rule["op"],
                _resolve_value(rule.get("value"), ctx),
            )
            for rule in any_rules
            if isinstance(rule, dict) and "attr" in rule and "op" in rule
        )

    return True


def evaluate_acl_entries(
    entries: list[AclEntryLike], ctx: AuthContext
) -> bool | None:
    if not entries:
        return None

    for entry in entries:
        if not match_conditions(entry.conditions, ctx):
            continue
        if entry.effect.value == "deny":
            return False
        return True

    return False
