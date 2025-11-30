import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class EasySpider(CrawlSpider):
    name = "easy"
    allowed_domains = ["web"]
    start_urls = ["https://www.gumtree.com/search?search_category=for-sale"]

    rules = (
      Rule(LinkExtractor(allow=r"Items/", restrict_xpaths='//*[@id="content"]//nav/ol/li//*[contains(@class, "pagination-link--next")]'), follow=True),
      Rule(LinkExtractor(restrict_xpaths='//*[@id="content"]//nav/ol/li//a[not(contains(@class, "pagination-link--next"))]/@href'), callback="parse_item"))

    def parse_item(self, response):
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item
