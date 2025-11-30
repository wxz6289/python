from asyncio import run, sleep, create_task, wait_for, TimeoutError
from delay import delay

async def main():
  delay_task = create_task(delay(1, "Hello"))
  try:
    result = await wait_for(delay_task, timeout= 2)
    print(result)
  except TimeoutError:
    print("got a timeout")
    print(f"Was the task cancelled? {delay_task.cancelled()}")

run(main())