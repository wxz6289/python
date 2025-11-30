# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from wikiSpider.items import Article
from string import whitespace
from datetime import datetime

class WikispiderPipeline:
    def process_item(self, article, spider):
        dateStr = article['last-updated']
        dateStr = dateStr.replace('本页面最后修订于', '')
        dateStr = dateStr.strip()
        dateStr = datetime.strptime(dateStr, '%d %B %Y, at %H:%M')
        article['last-updated'] = dateStr
        text = article['text']
        text = [line for line in text if line not in whitespace]
        article['text'] = ''.join(text)
        return article
