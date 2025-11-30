import smtplib

server = smtplib.SMTP("localhost")
server.sendmail("794838927.qq.com", "dreamingking@live.cn", "is ok?")
server.quit()
