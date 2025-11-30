# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item
from scrapy.item import Field


class PropertiesItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    price = Field()
    description = Field()
    address = Field()
    image_urls = Field()
    # calculate Filed
    images = Field()
    location = Field()

    # HouseKeeping
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

class BlogItem(Item):
  title = Field()
  date = Field()
  author = Field()
