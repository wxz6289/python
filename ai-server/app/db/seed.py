"""初始化 RBAC + ACL 演示数据。"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.domain.value_objects import AclEffect, SubjectType
from app.auth.infrastructure.models import (
    AclEntry,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)
from app.auth.infrastructure.security import hash_password
from app.db.session import close_db_engine, get_session_factory


async def seed() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        roles = {
            "admin": Role(code="admin", name="管理员", description="系统管理员"),
            "user": Role(code="user", name="普通用户", description="基础业务用户"),
            "guest": Role(code="guest", name="访客", description="只读访客"),
        }
        for role in roles.values():
            existing = await session.scalar(select(Role).where(Role.code == role.code))
            if existing is None:
                session.add(role)
        await session.flush()

        permissions = [
            Permission(
                code="chat:read",
                resource="chat",
                action="read",
                description="访问 /chat",
            ),
            Permission(
                code="chat:write",
                resource="chat",
                action="write",
                description="发起对话",
            ),
            Permission(
                code="item:read",
                resource="item",
                action="read",
                description="读取 items",
            ),
            Permission(
                code="item:write",
                resource="item",
                action="write",
                description="创建 items",
            ),
            Permission(
                code="ws:connect",
                resource="ws",
                action="connect",
                description="WebSocket 连接",
            ),
            Permission(
                code="user:manage",
                resource="user",
                action="*",
                description="用户管理",
            ),
        ]
        for permission in permissions:
            existing = await session.scalar(
                select(Permission).where(Permission.code == permission.code)
            )
            if existing is None:
                session.add(permission)
        await session.flush()

        role_rows = {
            role.code: await session.scalar(
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.code == role.code)
            )
            for role in roles.values()
        }
        permission_rows = {
            permission.code: await session.scalar(
                select(Permission).where(Permission.code == permission.code)
            )
            for permission in permissions
        }

        async def link_role_permission(role_code: str, permission_code: str) -> None:
            role = role_rows[role_code]
            permission = permission_rows[permission_code]
            if role is None or permission is None:
                return
            exists = await session.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )
            if exists is None:
                session.add(
                    RolePermission(role_id=role.id, permission_id=permission.id)
                )

        for permission in permission_rows:
            await link_role_permission("admin", permission)

        for code in ("chat:read", "chat:write", "item:read", "ws:connect"):
            await link_role_permission("user", code)

        await link_role_permission("guest", "item:read")

        users_spec = [
            ("alice", "secret123", "engineering", "user"),
            ("bob", "secret123", "sales", "admin"),
        ]
        for username, password, department, role_code in users_spec:
            user = await session.scalar(select(User).where(User.username == username))
            if user is None:
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    department=department,
                )
                session.add(user)
                await session.flush()

            role = role_rows[role_code]
            if role is not None:
                link = await session.scalar(
                    select(UserRole).where(
                        UserRole.user_id == user.id,
                        UserRole.role_id == role.id,
                    )
                )
                if link is None:
                    session.add(UserRole(user_id=user.id, role_id=role.id))

        await session.flush()

        alice = await session.scalar(select(User).where(User.username == "alice"))
        bob = await session.scalar(select(User).where(User.username == "bob"))
        if alice is not None:
            owner_rule = await session.scalar(
                select(AclEntry).where(
                    AclEntry.subject_type == SubjectType.USER,
                    AclEntry.subject_id == alice.id,
                    AclEntry.resource_type == "chat_session",
                    AclEntry.resource_id == "*",
                    AclEntry.action == "read",
                )
            )
            if owner_rule is None:
                session.add(
                    AclEntry(
                        subject_type=SubjectType.USER,
                        subject_id=alice.id,
                        resource_type="chat_session",
                        resource_id="*",
                        action="read",
                        effect=AclEffect.ALLOW,
                        conditions={
                            "all": [
                                {
                                    "attr": "resource.owner_id",
                                    "op": "eq",
                                    "value": "${user.id}",
                                }
                            ]
                        },
                        priority=10,
                    )
                )
                session.add(
                    AclEntry(
                        subject_type=SubjectType.USER,
                        subject_id=alice.id,
                        resource_type="chat_session",
                        resource_id="*",
                        action="write",
                        effect=AclEffect.ALLOW,
                        conditions={
                            "all": [
                                {
                                    "attr": "resource.owner_id",
                                    "op": "eq",
                                    "value": "${user.id}",
                                }
                            ]
                        },
                        priority=10,
                    )
                )

        if bob is not None:
            deny_rule = await session.scalar(
                select(AclEntry).where(
                    AclEntry.subject_type == SubjectType.USER,
                    AclEntry.subject_id == bob.id,
                    AclEntry.resource_type == "chat_session",
                    AclEntry.resource_id == "session-999",
                )
            )
            if deny_rule is None:
                session.add(
                    AclEntry(
                        subject_type=SubjectType.USER,
                        subject_id=bob.id,
                        resource_type="chat_session",
                        resource_id="session-999",
                        action="read",
                        effect=AclEffect.DENY,
                        priority=100,
                    )
                )

        await session.commit()
        print("RBAC + ACL seed completed.")


async def main() -> None:
    try:
        await seed()
    finally:
        await close_db_engine()


if __name__ == "__main__":
    asyncio.run(main())
