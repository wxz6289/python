import yagmail

server = yagmail.SMTP(user="kingdreaming@qq.com", password='pzepwobsdiycbdch', host="smtp.qq.com")

to = ['2395355749@qq.com',]
title = 'test'
content = 'This is a test'

server.send(to, title, content)
server.close()