import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as BS


class Content:
    def __init__(self, topic, url, title, body):
        self.topic = topic
        self.url = url
        self.title = title
        self.body = body

    def print(self):
        print(f"New article found for topic: {self.topic}")
        print(f"Title: { self.title}")
        print(f"Body: {self.body}")
        print(f"Url: {self.url}")


class WebSite:
    def __init__(
        self,
        name,
        url,
        searchUrl,
        resultListing,
        resultUrl,
        # absoluteUrl,
        titleTag,
        bodyTag,
    ):
        self.name = name
        self.url = url
        self.searchUrl = searchUrl
        self.resultListing = resultListing
        self.resultUrl = resultUrl
        # self.absoluteUrl = absoluteUrl
        self.titleTag = titleTag
        self.bodyTag = bodyTag


class Crawler:
    def __init__(self, headers={}):
        self.headers = headers
    def getPage(self, url):
        try:
            req = requests.get(url)
        except RequestException:
            return None
        return BS(req.text, "html.parser")

    def safeGet(self, pageObj, selector):
        childObj = pageObj.select(selector)
        if childObj is not None and len(childObj) > 0:
            return childObj[0].get_text()
        return ""

    def search(self, topic, site):
        bs = self.getPage(site.searchUrl + topic)
        searchResults = bs.select(site.resultListing)
        for result in searchResults:
            url = result.select(site.resultUrl)[0].attrs["href"]
            if site.absoluteUrl:
                bs = self.getPage(url)
            else:
                bs = self.getPage(site.url + url)

            if bs is None:
                print("Something was wrong with that page or URL. Skipping")
                return
            title = self.safeGet(bs, site.titleTag)
            body = self.safeGet(bs, site.bodyTag)
            if title != "" and body != "":
                content = Content(topic, title, body)
                content.print()


crawler = Crawler()
siteData = [
    [
        "慕课网",
        "https://www.imooc.com",
        "https://www.imooc.com/search/?words=",
        "div.search-course-list",
        "a.js-zhuge-allResult.item-title.js-result-item.js-item-title",
        True,
        "search-item.js-search-item",
        "div.item-desc"
    ]
]

sites = []

for row in siteData:
    sites.append(
        WebSite(*row)
    )

topics = ["python", "data science"]
for topic in topics:
    print("GETTING INFO ABOUT:" + topic)
    for targetSite in sites:
        crawler.search(topic, targetSite)
