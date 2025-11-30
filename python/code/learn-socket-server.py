import socket

s = socket.socket()
# AF_INET 地址族 SOCK_STREAM 流套接字(默认) SOCK_DGRAM 数据报套接字
host = socket.gethostname()
port = 1234
s.bind((host, port))

# 接收队列长度
s.listen(5)

while True:
  c, addr = s.accept() # 阻塞到连接到来
  print(f'Got connect from: {addr}')
  c.send(b"Thank you for connecting")
  c.close()