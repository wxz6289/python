from threading import Thread
import time

class Crawler(Thread):
  def __init__(self):
    Thread.__init__(self)
    print('init crawler')
    self.done = False

  def is_done(self):
    return self.done

  def run(self):
    time.sleep(5)
    self.done = True
    raise Exception('Something bad happened!')

t = Crawler()
t.start()

while True:
  time.sleep(1)
  if t.is_done():
    print('Done')
    break
  if not t.is_alive():
    t= Crawler()
    t.start()




