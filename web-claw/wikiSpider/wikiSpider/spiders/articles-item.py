import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from wikiSpider.items import Article

class ArticleSpider(CrawlSpider):
    name = "articles"
    allowed_domains = ['wikipedia.org']
    start_urls = ["https://zh.wikipedia.org/wiki/Javascript"]

    rules = [
      Rule(LinkExtractor(allow=(r'.*',)), callback='parse_items', follow=True),
      Rule(LinkExtractor(allow=('^(/wiki/)((?!:).)*$')), callback='parse_items')
      ]

    def parse_items(self, response):
        article = Article()
        article['url'] = response.url
        article['title'] = response.css('h1 span.mw-page-title-main::text').extract_first()
        article['text'] = response.xpath('//div[@id="mw-content-text"]//text()').extract()
        last_updated = response.css('li#footer-info-lastmod::text').extract_first()
        article['last_updated'] = last_updated.replace('本页面最后修订于', '')
        return article
