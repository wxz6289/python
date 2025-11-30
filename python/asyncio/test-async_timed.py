from delay import delay, async_timed
from asyncio import create_task, run

@async_timed()
async def main():
  task1 = create_task(delay(2))
  task2 = create_task(delay(5))
  await task1
  await task2

run(main())