import pymysql
from urllib.request import Request, urlopen
from urllib.parse import quote, unquote
from bs4 import BeautifulSoup as BS
from datetime import datetime
import random
import re


def store(title, content):
    cur.execute(
        f"INSERT INTO pages (title, content) VALUES (%s, %s)",
        (title.strip(), content.strip()),
    )
    cur.connection.commit()


def getLinks(base_url, article_url):
    response = urlopen(base_url + quote(article_url))
    content_type = response.headers.get_content_type()
    charset = response.headers.get_param('charset') or 'utf-8'
    content = response.read()
    html = content.decode(charset)
    bs = BS(html, "html.parser")
    title = bs.find("h1").get_text()
    content = bs.find("div", {"id": "mw-content-text"}).find("p").get_text()
    store(title, content)
    return bs.find("div", {"id": "bodyContent"}).find_all(
        "a", href=re.compile("^(/wiki/)((?!:).)*$")
    )


conn = pymysql.connect(
    host="localhost", user="king", password="king123", db="mysql", charset="utf8"
)
random.seed(datetime.timestamp(datetime.now()))
cur = conn.cursor()
cur.execute("use scraping")
base_url = "https://zh.wikipedia.org/"
links = getLinks(base_url, "/wiki/弗拉基米尔·普京")

try:
    while len(links) > 0:
        newArticle = links[random.randint(0, len(links) - 1)].attrs["href"]
        print(unquote(newArticle))
        links = getLinks(base_url, unquote(newArticle))
finally:
    cur.close()
    conn.close()
