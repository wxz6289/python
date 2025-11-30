from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import re
import random
from multiprocessing import Process
import time
import os

visited = []


def get_links(bs):
    print(f"Getting links in {os.getpid()}")
    links = bs.find("div", {"id": "bodyContent"}).find_all(
        "a", href=re.compile("^(/wiki/)((?!:).)*$")
    )
    return [link for link in links if link not in visited]


def scape_article(path):
    visited.append(path)
    print(f"Process {os.getpid()} list is now: {visited}")
    html = urlopen(f"http://en.wikipedia.org{path}")
    time.sleep(5)
    bs = BS(html, "html.parser")
    title = bs.find("h1").get_text()
    print(f"Scraping {title} in process {os.getpid()}")
    links = get_links(bs)
    if len(links) > 0:
        new_article = links[random.randint(0, len(links) - 1)].attrs["href"]
        print(new_article)
        scape_article(new_article)


if __name__ == "__main__":
    processes = []
    processes.append(Process(target=scape_article, args=("/wiki/Kevin_Bacon",)))
    processes.append(Process(target=scape_article, args=("/wiki/Monty_Python",)))

    for p in processes:
        p.start()
