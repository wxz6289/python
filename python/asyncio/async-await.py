from asyncio import run

async def my_counter() -> None:
  print("hello asyncio")

async def coroutine_add_one(number: int) -> int:
  return number + 1

def add_one(number: int) -> int:
  return number + 1

result3 = run(coroutine_add_one(1))
print("asyncio:", result3, type(result3))
result = add_one(2)
# result2 = await coroutine_add_one(1)
print("sync:",result, type(result))
# print("async:",result2, type(result2))

async def main():
  result = await coroutine_add_one(1)
  print("async:",result, type(result))

if __name__ == "__main__":
  run(main())

