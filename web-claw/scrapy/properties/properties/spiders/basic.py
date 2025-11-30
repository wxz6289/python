import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Join, MapCompose
import socket
from datetime import datetime
from properties.items import PropertiesItem


class BasicSpider(scrapy.Spider):
    name = "basic"
    allowed_domains = ["web"]
    start_urls = ["https://www.gumtree.com"]


  # def parse(self, response):
  #       item =PropertiesItem()
  #       title = response.xpath('//*[@class="grid-list-item"]//a/article//h2[@data-q="lisitingTitle"]/text()').extract()
  #       price = response.xpath('//div[@data-testid="price"]/text()').extract()
  #       self.log("title: %s" %  title)
  #       self.log("price: %s" % price)
  #       item['title'] = title
  #       item['price'] = price
  #       return item

    def parse(self, response):
      """
      This is spider for me
      @url https://www.gumtree.com
      @returns items 1
      @scrapes title price
      @scrapes url project spider server date

      """
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
