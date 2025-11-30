from urllib.request import urlopen
from bs4 import BeautifulSoup as BS

html = urlopen('https://blog.csdn.net/qq_40309183/article/details/80716637')
text = html.read().decode('utf-8', 'ignore')
soup = BS(text, 'html.parser');
# print(soup.prettify())
print(soup.title)
print(soup.h1)
print(soup.find_all('h1', class_="title-article"))
print(soup.find_all('div', class_="htmledit_views"))