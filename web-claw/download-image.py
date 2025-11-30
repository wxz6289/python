from urllib.request import urlretrieve, urlopen
from bs4 import BeautifulSoup as BS

html = urlopen('https://www.sohu.com/a/728408760_121660655')
bs = BS(html, 'html.parser')
image_urls = bs.find_all('img')
for image in image_urls:
  # print(image)
  try:
    image_url = image['src']
  except:
    image_url = '//p3.itc.cn/q_70/images03/20230213'+image['data-src']+'.jpeg'
  print(image_url)
  # urlretrieve(image_url, 'imgs/download' + image_url.split('/')[-1])

