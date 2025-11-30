import pymysql
from urllib.request import Request, urlopen
from urllib.parse import quote, unquote
from bs4 import BeautifulSoup as BS
from datetime import datetime
from random import shuffle
import random
import re


def insert_page_if_not_exists(url):
    cursor.execute("SELECT * FROM pages WHERE url = %s", (url))
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO pages(url) VALUES (%s)", (url))
        cursor.connection.commit()
        return cursor.lastrowid
    else:
        return cursor.fetchone()[0]


def load_pages():
    cursor.execute("SELECT * FROM pages")
    pages = [row[1] for row in cursor.fetchall()]
    return pages


def insert_link(from_page_id, to_page_id):
    cursor.execute(
        "SELECT * FROM links WHERE from_page_id = %s AND to_page_id = %s",
        (int(from_page_id), int(to_page_id))
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO links (from_page_id, to_page_id) VALUES (%s, %s)",
            (int(from_page_id), int(to_page_id))
        )
        cursor.connection.commit()


def get_links(base_url, page_url, pages, recursion_level):
    if recursion_level > 4:
        return
    page_id = insert_page_if_not_exists(page_url)
    print(page_url)
    response = urlopen(base_url + quote(page_url))
    content_type = response.headers.get_content_type()
    charset = response.headers.get_param("charset") or "utf-8"
    content = response.read()
    html = content.decode(charset)
    bs = BS(html, "html.parser")
    links = bs.find_all("a", href=re.compile("^(/wiki/)((?!:).)*$"))
    links = [link.attrs["href"] for link in links]
    for link in links:
        insert_link(page_id, insert_page_if_not_exists(link))
        if link not in pages:
            pages.append(link)
            get_links(base_url, link, pages, recursion_level + 1)


base_url = "https://en.wikipedia.org"
conn = pymysql.connect(
    host="localhost", user="king", password="king123", db="mysql", charset="utf8"
)
cursor = conn.cursor()

try:
    cursor.execute("USE wikipedia")
    get_links(base_url, "/wiki/Kevin_Bacon", load_pages(), 0)
finally:
    cursor.close()
    conn.close()
