# Scrapy

```bash
scrapy shell -s USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" https://www.gumtree.com
```

- xpath()
- css()

返回的都是Selector对象

## XPath

//div[@id="top"]

```bash
response.xpath('//*[@id="content"]/header/nav//div[@class="logo-text"]/svg').extract()
response.xpath('//h1/text()').extract()
response.xpath('//*[@class="h1"]/text()').extract()
response.xpath('//*[@data-testid="price"]/text()').re('[.0-9]+')
response.css('.grid-list-item a article div[data-testid="price"]').xpath('//div[@data-testid="price"]/text()').re('[.0-9]+')
```

scrapy底层依赖包

- lxml 高效的XML and HTML解析器
- parsel 基于lxml的HTML/XML数据抽取库
- w3lib 处理URL和编码的库
- twisted 网络框架库
- cryptograghy/pyOpenSSL 网络层安全的库

```bash
conda install -c conda-forge scrapy
pip install Scrapy
scrapy startproject propertices
cd propertiecs
# 使用模版创建爬虫
scrapy genspider basic web
scrapy genspider -l
# 选用模版
scrapy genspider -t
tree
scrapy crawl basic
scrapy parse --spider=basic https://www.gumtree.com
scrapy crawl basic -o item.json
scrapy crawl basic -o item.jl
scrapy crawl basic -o item.csv
scrapy crawl basic -o item.xml
pip install unicode
conda install python=3.12.4
pip install ipykernel
python -m ipykernel install --user --name=python3.12.4 --display-name python3.12.4
```

## contract

```bash
scrapy check basic
scrapy crawl manual -s CLOSESPIDER_TIMECOUNT=90

scrapy genspider -t crawl easy web
scrapy crawl easy -s CLOSESPIDER_TIMECOUNT=90

scrapy settings --get CONCURRENT_REQUESTS
scrapy settings --get CONCURRENT_REQUESTS -s CONCURRENT_REQUESTS=20

```

//*[@id="content"]//nav/ol/li/a[@class="pagination-link--next"]/@href
