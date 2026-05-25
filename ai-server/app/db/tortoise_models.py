"""Tortoise ORM 模型示例（与 SQLAlchemy 的 auth 表独立）。"""

from typing import Any

from tortoise.models import Model
from tortoise.fields import (
    CASCADE,
    CharField,
    DatetimeField,
    DecimalField,
    ForeignKeyField,
    ForeignKeyRelation,
    IntField,
    JSONField,
    ManyToManyField,
    ManyToManyRelation,
    OneToOneField,
    OneToOneRelation,
    TextField,
)


class Note(Model):
    """演示用记事本表，展示 Tortoise 与 MySQL 的基本 CRUD。"""

    id = IntField(primary_key=True)
    title = CharField(max_length=200)
    content = TextField(null=True)
    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "tortoise_notes"
        ordering = ["-created_at"]

class User(Model):
    """用户模型"""

    id = IntField(primary_key=True)
    email = CharField(max_length=20)
    username = CharField(max_length=20)
    password_hash = CharField(max_length=200)
    status = IntField(default=1) # 1: active, 0: deleted
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        table = "tortoise_users"
        ordering = ["-created_at"]
        indexes = ["email"]


class UserProfile(Model):
    """用户配置模型"""

    id = IntField(primary_key=True)
    profile_data = JSONField[dict[str, Any]]()
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
    user: OneToOneRelation[User] = OneToOneField(
        User,
        on_delete=CASCADE,
        related_name="profile",
    )

    class Meta:
        table = "tortoise_user_profiles"
        ordering = ["-created_at"]

class Product(Model):
    """产品模型"""

    id = IntField(primary_key=True)
    name = CharField(max_length=20)
    sku = CharField(max_length=20)
    status = IntField(default=1) # 1: active, 0: deleted
    description = TextField(null=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    stock = IntField(default=0)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        table = "tortoise_products"
        ordering = ["-created_at"]

class Order(Model):
    """订单模型"""

    id = IntField(primary_key=True)
    order_no = CharField(max_length=20)
    user: ForeignKeyRelation[User] = ForeignKeyField(User, on_delete=CASCADE, related_name="orders")
    status = IntField(default=1) # 1: pending, 2: paid, 3: shipped, 4: delivered, 5: completed  6: cancelled
    # products: ManyToManyRelation[Product] = ManyToManyField(Product, related_name="orders", through="app.db.tortoise_models.OrderItem")
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        table = "tortoise_orders"
        ordering = ["-created_at"]


class OrderItem(Model):
    """订单产品模型"""

    id = IntField(primary_key=True)
    # order_id = IntField()
    # product_id = IntField()
    order: ForeignKeyRelation[Order] = ForeignKeyField(Order, on_delete=CASCADE, related_name="product")
    product: ForeignKeyRelation[Product] = ForeignKeyField(Product, on_delete=CASCADE, related_name="order")
    quantity = IntField(default=1)
    price = DecimalField(max_digits=10, decimal_places=2)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        table = "tortoise_order_items"
        unique_together = ["order", "product"]
        ordering = ["-created_at"]
