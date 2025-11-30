import asyncio
from delay import delay
import time

async def hello(message: str, second: int):
  for i in range(3):
    await delay(second, message)
    print(f"{message} I'm running other code while I'm waiting!")


async def main():
  t1 = time.time()
  task1 = asyncio.create_task(hello("Hello king", 1))
  task2 = asyncio.create_task(hello("hi dreamer", 1.5))
  await task1
  await task2

asyncio.run(main())