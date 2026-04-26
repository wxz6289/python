# scrapy

```bash
scrapy startproject wikiSpider
scrapy genspider example example.com
scrapy runspider article-items.py -o articles.json -t json
scrapy crawl articles -s LOG_FILE=wiki.log
```

《精通Python爬虫框架Scrapy》 Dimitrios Kouzis-Loukas

游标 一个游标跟踪一种状态信息，还会包含最后一次查询执行的结果。 一个连接可以有多个游标。

修改编码

```sql
ALTER DATABASE scraping CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
ALTER TABLE pages CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE pages CHANGE title title VARCHAR(200) CHARACTER  SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE pages CHANGE content content VARCHAR(10000) CHARACTER  SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Pillow PIL 图像处理库

Tesseract 对渐变背景色处理比较弱， 对带有大片空白，带标题的等问题的图片需要进行预处理

Tor 代理服务器 IP地址隐匿手段
PySocks

[chrome](https://googlechromelabs.github.io/chrome-for-testing/
)
