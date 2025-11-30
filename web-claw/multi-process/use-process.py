from multiprocessing import Process
import time
import os


def print_time(thread_name, delay, iterations):
    start_time = int(time.time())
    for i in range(0, iterations):
        time.sleep(delay)
        seconds_elapsed = str(int(time.time()) - start_time)
        print(thread_name if thread_name else seconds_elapsed)


if __name__ == "__main__":
    processes = []
    processes.append(Process(target=print_time, args=("Counter", 1, 100)))
    processes.append(Process(target=print_time, args=("Fizz", 3, 33)))
    processes.append(Process(target=print_time, args=("Buzz", 5, 20)))

    for p in processes:
        p.start()
    print('start')
    for p in processes:
        p.join()
    print('end')
print(f"ppid: {os.getppid()} and pid: {os.getpid()}")
