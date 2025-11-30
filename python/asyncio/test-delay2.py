import asyncio
from delay import delay
import time

async def hello(message: str, second: int) -> str:
  await delay(second)
  return message

async def add_one(number: int) -> int:
  await delay(number)
  return number + 1

async def main():
  t1 = time.time()
  task1 = asyncio.create_task(hello("Hello king", 2))
  task2 = asyncio.create_task(add_one(1))
  print(type(task1))
  message = await task1
  result = await task2
  print(message)
  print(result)
  t2 = time.time()
  print("t2-t1:", t2 - t1)

asyncio.run(main())