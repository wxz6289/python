from csv import writer
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS

html = urlopen('https://zh.wikipedia.org/wiki/%E4%BB%A5%E8%89%B2%E5%88%97')
bs = BS(html, 'html.parser')
table = bs.findAll('table', { 'class': 'wikitable'})[0]
rows = table.findAll('tr')
with open('test.csv', '+w') as csv_file:
  writer = writer(csv_file)
  for row in rows:
    csv_row = []
    for cell in row.findAll(['td', 'th']):
      csv_row.append(cell.get_text().strip())
    writer.writerow(csv_row)
