"""Tortoise ORM 模型示例（与 SQLAlchemy 的 auth 表独立）。"""

from tortoise import fields, models


class Note(models.Model):
    """演示用记事本表，展示 Tortoise 与 MySQL 的基本 CRUD。"""

    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tortoise_notes"
