import threading
import time

def crawler(url):
    data = threading.local()
    data.visited = []
    print(f"scraping {url}")

# threading.Thread(target=crawler, args=("http://brooking.edu",)).start()

t = threading.Thread(target=crawler, args=("http://brooking.edu",))
t.start()

while True:
  time.sleep(1)
  if not t.is_alive():
    t= threading.Thread(target=crawler, args=("http://brooking.edu",))
    t.start()




