import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from properties.items import BlogItem



class NodeBlogSpider(CrawlSpider):
    name = "node_blog"
    allowed_domains = ["web"]
    start_urls = ["https://nodejs.org/en/blog"]

    # rules = (
    #   Rule(LinkExtractor(allow=r"Items/", restrict_xpaths='//*[@id="content"]//nav/ol/li//*[contains(@class, "pagination-link--next")]'), follow=True),
    #   Rule(LinkExtractor(restrict_xpaths='//*[@id="content"]//nav/ol/li//a[not(contains(@class, "pagination-link--next"))]/@href'), callback="parse_item"))

    def parse_item(self, response):
        item = BlogItem()
        title = response.xpath('//*[contains(@class, "BlogPostCard_title")]/text()').get()
        author = response.xpath('//*[contains(@class, "BlogPostCard_author")]/p/text()').get()
        date = response.xpath('//*[contains(@class, "BlogPostCard_author")]/time/@datetime').get()
        item.title = title
        item.author = author
        item.date = date
        print("LLLLL>>>>", title, author, date)
        return item
