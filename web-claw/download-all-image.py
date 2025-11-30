from urllib.request import urlretrieve, urlopen
from bs4 import BeautifulSoup as BS
from os import makedirs
from os.path import dirname, exists
from re import compile

download_dir = 'downloaded'
base_url = 'https://www.nipic.com'

def get_absolute_url(base_url, source):
  if source.startswith('https://www.'):
    url = f'https://{source[12:]}'
  elif source.startswith('https://'):
    url = source
  elif source.startswith('//'):
    url = f'https:{source}'
  elif source.startswith('www.'):
    url = source[4:]
    url = f'https://{source}'
  else:
    url = f'{base_url}/{source}'

  # if base_url not in url:
    # return None
  return url

def get_download_path(base_url, absolute_url, download_dir):
  path = absolute_url.replace('www', '')
  path = path.replace(base_url, '')
  path = download_dir + '/' + path
  directory = dirname(path)
  if not exists(directory):
    makedirs(directory)

  return path

html = urlopen(r'https://www.sohu.com/a/728408760_121660655')
bs = BS(html, 'html.parser')
download_list = bs.find_all('img')
# print(download_list)
image_pattern = compile(r'.*\.(jpg|png|jpeg)$')
for download in download_list:
  file_url = get_absolute_url(base_url, download['src'])
  if file_url is not None and image_pattern.match(file_url):
    print(file_url)
    urlretrieve(file_url, get_download_path(base_url, file_url, download_dir))
