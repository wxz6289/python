from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
html = urlopen('http://gz.people.com.cn/n2/2024/0626/c222152-40891196.html')

soup = BS(html, 'html.parser')
# print(soup.prettify())
# print(soup.title, soup.title.name)
# print(soup.title.parent.name)
# print(soup.find_all('a'))
# images = soup.find_all('img')
# for image in images:
#   print(image.get('src'))
# print(soup.find_all('img'))
# contents = soup.find_all('div')
# print(soup.body)
contents = soup.body.find_all('div', class_="rm_txt")
print(len(contents))
for content in contents:
  if content is not None:
    print(content.string)
