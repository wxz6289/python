from threading import Thread
import time


def print_time(thread_name, delay, iterations):
    start_time = int(time.time())
    for i in range(0, iterations):
        time.sleep(delay)
        seconds_elapsed = str(int(time.time()) - start_time)
        print(f"{seconds_elapsed} {thread_name}")

Thread(target=print_time, args=("Fizz", 3, 33)).start()
Thread(target=print_time, args=("Buzz", 5, 20)).start()
Thread(target=print_time, args=("Counter", 1, 100)).start()

# threading.local() 创建线程内部局部数据