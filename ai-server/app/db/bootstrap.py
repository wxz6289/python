"""创建数据库并初始化 RBAC + ACL 表结构。"""

from __future__ import annotations

import asyncio
from pathlib import Path

import aiomysql

from app.config import get_settings
from app.db.session import close_db_engine

INIT_SQL = Path(__file__).with_name("init.sql")


async def bootstrap() -> None:
    settings = get_settings()
    conn = await aiomysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        autocommit=True,
    )
    try:
        async with conn.cursor() as cursor:
            db_name = settings.mysql_database.replace("`", "")
            await cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            await cursor.execute(f"USE `{db_name}`")
            sql = INIT_SQL.read_text(encoding="utf-8")
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    await cursor.execute(stmt)
    finally:
        conn.close()

    print(f"Database `{settings.mysql_database}` initialized.")


async def main() -> None:
    try:
        await bootstrap()
    finally:
        await close_db_engine()


if __name__ == "__main__":
    asyncio.run(main())
