from  asyncio import sleep
from functools import wraps
from time import time
from typing import Callable, Any

def async_timed():
  def wrapper(fn: Callable) -> Callable:
    @wraps(fn)
    async def wrapped(*args, **kwargs) -> Any:
      print(f"starting {fn.__name__}() with args {args} {kwargs}")
      start = time()
      try:
        return await fn(*args, **kwargs)
      finally:
        end = time()
        total = end - start
        print(f"finished {fn.__name__}() in {total:.4f}s")
    return wrapped
  return wrapper

@async_timed()
async def delay(duration: int, tips = "") -> int:
  print(f"{tips} sleeping for {duration} seconds")
  await sleep(duration)
  print(f"{tips} finished sleeping for {duration} seconds")
  return duration