import scrapy


class ArticleSpider(scrapy.Spider):
    name = "article"

    def start_requests(self):
      urls = ["https://zh.wikipedia.org/wiki/Python",
              "https://zh.wikipedia.org/wiki/Javascript"
              ]
      return [scrapy.Request(url=url, callback=self.parse) for url in urls]

    def parse(self, response):
        url = response.url
        title = response.css('h1 span.mw-page-title-main::text').extract_first()
        print(f'URL is {url}')
        print(f'Title is {title}')
