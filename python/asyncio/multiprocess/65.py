from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import time
import asyncio
from asyncio.events import AbstractEventLoop
from typing import List

def count(count_to: int) -> int:
  start = time.time()
  counter = 0
  while counter < count_to:
    counter =  counter + 1

  end = time.time()
  print(f'Finished counting to {count_to} in { end - start}')
  return counter


async def main():
  with ProcessPoolExecutor() as process_pool:
    loop: AbstractEventLoop = asyncio.get_running_loop()
    nums = [1, 3, 5, 22, 1000000]
    calls: List[partial[[int]]] = [partial(count, num) for num in nums]
    call_cors = []

    for call in calls:
      call_cors.append(loop.run_in_executor(process_pool, call))

    # results = await asyncio.as_completed(*call_cors)
    results = await asyncio.gather(*call_cors)
    for result in results:
      print(result)

if __name__ == '__main__':
  asyncio.run(main())
