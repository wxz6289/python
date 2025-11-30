from asyncio import run, sleep, create_task, shield, wait_for, TimeoutError
from delay import delay

async def main():
  delay_task = create_task(delay(2, "Hello"))
  try:
    result = await wait_for(shield(delay_task), timeout= 1)
    print(result)
  except TimeoutError:
    print("got a timeout")
    print(f"Was the task cancelled? {delay_task.cancelled()}")
    print("Task took longer, it will finished soon!")
    result = await delay_task
    print(result)

run(main())