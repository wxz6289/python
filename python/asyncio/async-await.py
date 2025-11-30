import asyncio

async def my_counter() -> None:
  print("hello asyncio")

async def coroutine_add_one(number: int) -> int:
  return number + 1

def add_one(number: int) -> int:
  return number + 1

result3 = asyncio.run(coroutine_add_one(1))
print("asyncio:", result3, type(result3))
result = add_one(1)
result2 = coroutine_add_one(1)
print("sync:",result, type(result))
print("async:",result2, type(result2))

