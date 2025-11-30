from asyncio import run, sleep, create_task, CancelledError
from delay import delay

async def main():
  long_task = create_task(delay(10, "Hello"))
  seconds = 0

  while not long_task.done():
    print("Task not finished, checking again in a second")
    await sleep(1)
    seconds += 1
    if seconds == 5:
      long_task.cancel() # 不会立即停止任务，只有当前处于等待点或下一个等待点才会停止任务

  try:
    await long_task
  except CancelledError:
    print("long task was cancelled")

run(main())