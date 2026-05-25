from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.value_objects import SubjectType
from app.auth.infrastructure.models import AclEntry


async def fetch_acl_entries(
    session: AsyncSession,
    *,
    user_id: int,
    role_ids: list[int],
    resource_type: str,
    resource_id: str,
    action: str,
) -> list[AclEntry]:
    subject_filters = [(SubjectType.USER, user_id)]
    subject_filters.extend((SubjectType.ROLE, role_id) for role_id in role_ids)

    stmt = (
        select(AclEntry)
        .where(AclEntry.resource_type == resource_type)
        .where(or_(AclEntry.resource_id == resource_id, AclEntry.resource_id == "*"))
        .where(or_(AclEntry.action == action, AclEntry.action == "*"))
        .where(
            or_(
                *[
                    (AclEntry.subject_type == subject_type)
                    & (AclEntry.subject_id == subject_id)
                    for subject_type, subject_id in subject_filters
                ]
            )
        )
        .order_by(AclEntry.priority.desc(), AclEntry.id.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
