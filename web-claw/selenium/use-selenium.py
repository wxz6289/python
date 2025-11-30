from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib3
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('/opt/chromedriver')

try:
  # driver.set_window_size(1920,1080)
  driver.get('https://www.zhipin.com/hangzhou/')
  print(driver.title)
  driver.implicitly_wait(2)
  search_bar = driver.find_element(by=By.NAME, value="query")
  search_bar.clear()
  submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button.btn-search")
  search_bar.send_keys('前端')
  time.sleep(2)
  submit_button.click()
  results = driver.find_element(by=By.CSS_SELECTOR, value='ul.job-list-box')
  print(results)
  list_jobs = results.find_element(by=By.CSS_SELECTOR, value="li.job-card-wrapper")
  print(list_jobs)
  # search_bar.send_keys(Keys.RETURN)
  # print(driver.current_url)
  # print(driver.window_handles)
  # try:
  #   element = WebDriverWait(driver, 5).until(
  #   EC.presence_of_element_located((By.ID, "id-of-new-element"))
  #   )
  # except:
  #   pass
  time.sleep(60)
finally:
  driver.quit()

# CSS ID: .find_element_by_id(“id-search-field”)
# DOM Path: .find_element_by_xpath(“//input[@id=’id-search-field’]”)
# CSS class: .find_element_by_class_name(“search-field”)
# driver.switch_to_window('window_name')
# .switch_to_frame()
# driver.switch_to_default_content()
# 等待策略
# driver.implicitly_wait(5)
# 发送命令 与元素相关

# drag_and_drop(source,target)
# context_click(on_element)
# double_click(on_element)
# send_keys(keys_to_send)

# boss列表接口
# https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&query=%E5%89%8D%E7%AB%AF&city=101210100&experience=&payType=&partTime=&degree=&industry=&scale=&stage=&position=&jobType=&salary=&multiBusinessDistrict=&multiSubway=&page=1&pageSize=30
# https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=2&query=%E5%89%8D%E7%AB%AF&city=101210100&page=1&pageSize=100
