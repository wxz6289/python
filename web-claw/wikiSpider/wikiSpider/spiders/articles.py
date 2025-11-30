import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class ArticleSpider(CrawlSpider):
    name = "articles"
    allowed_domains = ['wikipedia.org']
    start_urls = ["https://zh.wikipedia.org/wiki/Javascript"]

    rules = [
      Rule(LinkExtractor(allow=(r'.*',)), callback='parse_items', cb_kwargs={'is_article': True }, follow=True),
      Rule(LinkExtractor(allow=('^(/wiki/)((?!:).)*$')), callback='parse_items', cb_kwargs={'is_article': False })
      ]

    def parse_items(self, response, is_article):
        url = response.url
        title = response.css('h1 span.mw-page-title-main::text').extract_first()
        if is_article:
          text = response.xpath('//div[@id="mw-content-text"]//text()').extract()
          last_updated = response.css('li#footer-info-lastmod::text').extract_first()
          last_updated = last_updated.replace('本页面最后修订于', '')
          print(f'URL is {url}')
          print(f'Title is {title}')
          print(f'text is {text}')
          print(f'Last Modified is {last_updated}')
        else:
          print("This is not an article: {title }")
