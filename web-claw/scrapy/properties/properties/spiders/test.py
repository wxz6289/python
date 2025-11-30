from scrapy import Spider
from scrapy.item import Item, Field
from datetime import datetime


class HooksAsyncItem(Item):
    name = Field()
    date = Field()


class TestSpider(Spider):
    name = "test"
    allowed_domains = ["example.com"]
    start_urls = ('http://www.example.com',)

    def parse(self, response):
        for i in range(2):
            item = HooksAsyncItem()
            item.name = "Hello %d" % i
            item.date = datetime.now()
            yield item
        raise Exception("dead")
