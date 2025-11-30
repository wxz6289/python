import time
import asyncio
from functools import partial, reduce
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict
from c6_14 import partition, map_frequencies, merge_dictionaries

async def reduce(loop, pool, counters, chunk_size) -> Dict[str,int]:
  chunks: List[List[Dict]] = list(partition(counters, chunk_size))
  reducers = []

async def main(partition_size: int):
  with open('./googlebooks-eng-all-1gram-20120701-a', encoding='utf-8') as f:
    contents = f.readlines()
    loop = asyncio.get_running_loop()
    tasks = []
    start = time.time()
    with ProcessPoolExecutor() as pool:
      for chunk in partition(contents, partition_size):
        tasks.append(loop.run_in_executor(pool, partial(map_frequencies, chunk)))
      intermediate_results = await asyncio.gather(*tasks)
      final_result = reduce(merge_dictionaries, intermediate_results)
      print(f"Aardvark has appeared {final_result['Aardvark']} times.")
      end = time.time()
      print(f'MapReduce took: { end - start: .4f} seconds')

if __name__ == '__main__':
  asyncio.run(main(partition_size=60000))
