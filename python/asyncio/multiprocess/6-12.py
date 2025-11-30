from multiprocessing import Process, Value, Array
from concurrent.futures import ProcessPoolExecutor
import asyncio

shared_counter: Value

def init(counter: Value):
  global shared_counter
  shared_counter = counter

def increment_value():
  with shared_counter.get_lock():
    shared_counter.value += 1

async def main():
  counter = Value('i', 0)
  with ProcessPoolExecutor(initializer=init, initargs=(counter,)) as pool:
    await asyncio.get_running_loop().run_in_executor(pool, increment_value)

    print(counter.value)
    # assert(counter.value == 2)

if __name__ == "__main__":
  asyncio.run(main())
