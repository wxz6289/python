from asyncio import Future, create_task, sleep, run

def make_request() -> Future:
  future = Future()
  create_task(set_future_value(future))
  return future

async def set_future_value(future):
  await sleep(2)
  future.set_result(23)

async def main():
  future = make_request()
  print(f"future status: {future.done()}")
  value = await future
  print(f"future status again: {future.done()}")
  print(value)

run(main())