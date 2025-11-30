import _thread as th
import time

def print_time(thread_name, delay, iterations):
  start_time = int(time.time())
  for i in range(0, iterations):
    time.sleep(delay)
    seconds_elapsed = str(int(time.time()) - start_time)
    print(f'{seconds_elapsed} {thread_name}')

try:
  th.start_new_thread(print_time, ('Fizz', 3, 33))
  th.start_new_thread(print_time, ('Buzz', 5, 20))
  th.start_new_thread(print_time, ('Counter', 1, 100))
except:
  print('Error: unable to start thread')

while 1:
  pass