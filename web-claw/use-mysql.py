import pymysql
conn = pymysql.connect(host="localhost", user='king', password='king123', db='mysql')

cur = conn.cursor()
cur.execute('use scraping')
cur.execute('select * from pages where id=1')
print(cur.fetchone())
cur.close()
conn.close()