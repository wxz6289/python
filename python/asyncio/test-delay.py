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
  message = await hello("Hello king", 2)
  print(message)
  t2 = time.time()
  print("t2-t1:", t2 - t1)

  result = await add_one(1)
  print(result)
  t3 = time.time()
  print("t3-t1:", t3 - t1)


asyncio.run(main())