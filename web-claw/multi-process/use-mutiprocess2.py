from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import re
import random
from multiprocessing import Process, Queue
import time
import os


def task_delegator(task_queue, urls_queue):
    visited = ["/wiki/Kevin_Bacon", "/wiki/Monty_Python"]
    task_queue.put("/wiki/Kevin_Bacon")
    task_queue.put("/wiki/Monty_Python")

    while 1:
        if not urls_queue.empty():
            links = [link for link in urls_queue.get() if link not in visited]
            for link in links:
                task_queue.put(link)


def get_links(bs):
    print(f"Getting links in {os.getpid()}")
    links = bs.find("div", {"id": "bodyContent"}).find_all(
        "a", href=re.compile("^(/wiki/)((?!:).)*$")
    )
    return [link.attrs["href"] for link in links]


def scape_article(task_queue, urls_queue):
    while 1:
        while task_queue.empty():
            time.sleep(0.1)

        path = task_queue.get()
        html = urlopen(f"http://en.wikipedia.org{path}")
        time.sleep(5)
        bs = BS(html, "html.parser")
        title = bs.find("h1").get_text()
        print(f"Scraping {title} in process {os.getpid()}")
        links = get_links(bs)
        urls_queue.put(links)

if __name__ == "__main__":
    processes = []
    task_queue = Queue()
    urls_queue = Queue()
    processes.append(Process(target=task_delegator, args=(task_queue, urls_queue)))
    processes.append(Process(target=scape_article, args=(task_queue, urls_queue)))
    processes.append(Process(target=scape_article, args=(task_queue, urls_queue)))

    for p in processes:
        p.start()
