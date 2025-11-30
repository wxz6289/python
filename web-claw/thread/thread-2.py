from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import re
import random
import _thread as thread
import time

visited = []
def get_links(thread_name, bs):
  print(f"Getting links in {thread_name}")
  links = bs.find('div', { 'id': 'bodyContent'}).find_all('a', href=re.compile('^(/wiki/)((?!:).)*$'))
  return [link for link in links if link not in visited]

def scape_article(thread_name, path):
  visited.append(path)
  html = urlopen(f'http://en.wikipedia.org{path}')
  time.sleep(5)
  bs = BS(html, 'html.parser')
  title = bs.find('h1').get_text()
  print(f'Scraping {title} in thread {thread_name}')
  links = get_links(thread_name, bs)
  if len(links) > 0:
    new_article = links[random.randint(0, len(links) - 1)].attrs['href']
    print(new_article)
    scape_article(thread_name, new_article)

try:
  thread.start_new_thread(scape_article, ('Thread 1', '/wiki/Kevin_Bacon',))
  thread.start_new_thread(scape_article, ('Thread 2', '/wiki/Monty_Python',))
except:
  print('Error: unable to start thread')

while 1:
  pass