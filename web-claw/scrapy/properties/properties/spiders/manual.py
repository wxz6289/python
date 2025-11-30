import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Join, MapCompose
import socket
from datetime import datetime
from properties.items import PropertiesItem
from os.path import join


class ManualSpider(scrapy.Spider):
    name = "manual"
    allowed_domains = ["web"]
    start_urls = ["https://www.gumtree.com"]


    def parse(self, response):
      """
      This is spider for me
      @url https://www.gumtree.com
      @returns items 1
      @scrapes title price
      @scrapes url project spider server date

      """
      next_selector = response.xpath('//*[@id="content"]//nav/ol/li//a[contains(@class, "pagination-link--next")]/@href')
      for url in next_selector.extract():
        yield Request(join(response.url, url))

      item_selector = response.xpath('//*[@id="content"]//nav/ol/li//a[not(contains(@class, "pagination-link--next"))]/@href')
      for url in item_selector.extract():
        yield Request(join(response.url, url), callback=self_parse_item)

      l = ItemLoader(item = PropertiesItem(), response = response)
      l.add_xpath('title', '//*[@data-q="lisitingTitle"]/text()', MapCompose(str.strip, str.title))
      l.add_xpath('price', '//*[@data-testid="price"]/text()', MapCompose(lambda s: s.replace(',', ''), float), re='[,.0-9]+', )
      l.add_xpath('description', '//*[@class="css-128qgph ekk5mp18"]/text()')
      l.add_xpath('address', '//*[@class="css-1s31ptg ekk5mp12"]/span/text()')
      l.add_xpath('image_urls', '//figure[@class="listing-tile-thumbnail-image"]/img/@src')
      l.add_value('url', response.url)
      l.add_value('project', self.settings.get('BOT_NAME'))
      l.add_value('spider', self.name)
      l.add_value('server', socket.gethostname())
      l.add_value('date', datetime.now())
      return l.load_item()
