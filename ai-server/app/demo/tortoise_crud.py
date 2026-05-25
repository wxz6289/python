import asyncio
from typing import List
from datetime import datetime
from app.db.tortoise_models import User, Product, Order, OrderItem
from tortoise import Tortoise
from app.db.tortoise_config import close_tortoise_orm, init_tortoise_orm

async def get_all_users() -> List[User]:
    return await User.all()

async def get_user_by_name(username: str) -> list[User]:
    return await User.filter(username__contains=username)

async def get_all_products() -> List[Product]:
    return await Product.all()

async def get_product_by_sku(sku: str) -> list[Product]:
    return await Product.filter(sku__contains=sku)

async def get_all_orders() -> List[Order]:
    return await Order.all()

async def get_order_by_order_no(order_no: str) -> list[Order]:
    return await Order.filter(order_no__contains=order_no)

async def get_all_order_items() -> List[OrderItem]:
    return await OrderItem.all()

async def get_order_item_by_order_id(order_id: int) -> list[OrderItem]:
    return await OrderItem.filter(order_id=order_id)

async def get_order_item_by_product_id(product_id: int) -> list[OrderItem]:
    return await OrderItem.filter(product_id=product_id)

async def create_product(product: Product) -> Product:
    await product.save()
    return product

async def create_order(order: Order) -> Order:
    await order.save()
    return order

async def create_order_item(order_item: OrderItem) -> OrderItem:
    await order_item.save()
    return order_item

async def update_product(product: Product) -> Product:
    updated = await product.filter(id=product.id)
    updated[0].name = product.name
    updated[0].sku = product.sku
    updated[0].price = product.price
    updated[0].stock = product.stock
    await updated[0].save()
    return updated[0]

async def update_order(order: Order) -> Order:
    updated = await order.filter(id=order.id)
    updated[0].order_no = order.order_no
    updated[0].status = order.status
    await updated[0].save()
    return updated[0]

async def update_order_item(order_item: OrderItem) -> OrderItem:
    updated = await order_item.filter(id=order_item.id)
    updated[0].quantity = order_item.quantity
    updated[0].price = order_item.price
    await updated[0].save()
    return updated[0]

async def create_user(user: User) -> User:
    await user.save()
    return user

async def create_product(product: Product) -> Product:
    await product.save()
    return product

async def create_order(order: Order) -> Order:
    await order.save()
    return order

async def create_order_item(order_item: OrderItem) -> OrderItem:
    await order_item.save()
    return order_item

async def update_product(product: Product) -> Product:
    updated = await product.filter(id=product.id)
    updated[0].name = product.name
    updated[0].sku = product.sku
    updated[0].price = product.price
    updated[0].stock = product.stock
    await updated[0].save()
    return updated[0]

async def update_order(order: Order) -> Order:
    updated = await order.filter(id=order.id)
    updated[0].order_no = order.order_no
    updated[0].status = order.status
    await updated[0].save()
    return updated[0]

async def update_order_item(order_item: OrderItem) -> OrderItem:
    updated = await order_item.filter(id=order_item.id)
    updated[0].quantity = order_item.quantity
    updated[0].price = order_item.price
    await updated[0].save()
    return updated[0]

async def delete_product(product_id: int) -> None:
    await Product.filter(id=product_id).delete()

async def delete_order(order_id: int) -> None:
    await Order.filter(id=order_id).delete()

async def delete_order_item(order_item_id: int) -> None:
    await OrderItem.filter(id=order_item_id).delete()
async def get_user(user_id: int) -> User:
    return await User.get(id=user_id)


async def update_user(user: User) -> User:
  updated = await user.filter(id=user.id)
  updated[0].email = user.email
  updated[0].username = user.username
  updated[0].password_hash = user.password_hash
  await updated[0].save()
  return updated[0]


async def delete_user(user_id: int) -> None:
  await User.filter(id=user_id).delete()

async def init_db():
  await init_tortoise_orm()

async def close_db():
  await close_tortoise_orm()

async def main():
  await init_db()
  # await create_user(User(email="wxz@gmail.com", username="wxz", password="123456"))
  # users = await get_all_users()
  # print([{"email": user.email, "username": user.username, "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")} for user in users])
  # user = await get_user(1)
  # print(user.email, user.username, user.created_at.strftime("%Y-%m-%d %H:%M:%S"))

  # updated_user = await update_user(User(id=2, email="wxz2@gmail.com", username="wxz2", password="123456"))

  # print(updated_user.email, updated_user.username, updated_user.created_at.strftime("%Y-%m-%d %H:%M:%S") if updated_user.created_at else None)
  users = await get_user_by_name("wxz")
  print([{"email": user.email, "username": user.username, "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")} for user in users])
  await close_db()

if __name__ == "__main__":
  asyncio.run(main())
