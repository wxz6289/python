import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header

msg = MIMEText('hi! this is from python!', 'plain','utf-8')

msg['Subject'] = Header('An Email Alert', 'utf-8')
msg['From'] = 'King <kingdreaming@qq.com>'
msg['To'] = Header('2395355749@qq.com', 'utf-8')

try:
  smtp = smtplib.SMTP('smtp.qq.com', 587)
  context = ssl.create_default_context()
  smtp.ehlo()
  smtp.starttls(context=context)  # Secure the connection
  smtp.ehlo()
  # smtp.connect('smtp.qq.com')
  # // pzepwobsdiycbdch
  smtp.set_debuglevel(1)
  smtp.login('kingdreaming@qq.com', 'pzepwobsdiycbdch')
  # smtp.login('794848927@qq.com', '794838927Mn')
  smtp.send_message(msg, from_addr='kingdreaming@qq.com', to_addrs=['2395355749@qq.com'])
  # smtp.sendmail('kingdreaming@qq.com', '2395355749@qq.com', msg.as_string())
except Exception as e:
  print(e)
finally:
  smtp.quit()