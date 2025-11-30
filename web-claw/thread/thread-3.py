from urllib.request import urlopen
from queue import Queue
from bs4 import BeautifulSoup as BS
import _thread as thread
import re
import random
import time
import pymysql


def storage(queue):
  conn = pymysql.connect(host="localhost", user="king", password="king123", db="mysql", charset="utf8")
  cursor = conn.cursor()
  cursor.execute('USE wiki_threads')
  while 1:
    if not queue.empty():
      article = queue.get()
      cursor.execute('SELECT * FROM pages WHERE path = %s', article['path'])
      if cursor.rowcount == 0:
        print(f'Storing article {article['title']}')
        cursor.execute('INSERT INTO pages (title, path) VALUES (%s, %s)', (article['title'], article['path']))
        conn.commit()
      else:
        print(f'Article already exists: {article['title']}')

visited = []
def get_links(thread_name, bs):
  print(f"Getting links in {thread_name}")
  links = bs.find('div', { 'id': 'bodyContent'}).find_all('a', href=re.compile('^(/wiki/)((?!:).)*$'))
  return [link for link in links if link not in visited]

def scape_article(thread_name, path, queue):
  visited.append(path)
  html = urlopen(f'http://en.wikipedia.org{path}')
  time.sleep(5)
  bs = BS(html, 'html.parser')
  title = bs.find('h1').get_text()
  print(f'Added {title} for storage in thread {thread_name}')
  queue.put({ 'title': title, 'path': path })
  links = get_links(thread_name, bs)
  if len(links) > 0:
    new_article = links[random.randint(0, len(links) - 1)].attrs['href']
    print(new_article)
    scape_article(thread_name, new_article, queue)

queue = Queue()
try:
  thread.start_new_thread(scape_article, ('Thread 1', '/wiki/Kevin_Bacon', queue))
  thread.start_new_thread(scape_article, ('Thread 2', '/wiki/Monty_Python', queue))
  thread.start_new_thread(storage, (queue,))
except:
  print('Error: unable to start thread')

while 1:
  pass