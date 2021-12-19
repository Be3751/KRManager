from selenium import webdriver
import time
from private_val import EMAIL, PWD

root = 'http://localhost:8080/notify/'
target = root + 'auth/'
driver = webdriver.Safari()
driver.get(target)

current_url = driver.current_url # 現在のURLを取得
if not current_url == target:
    print('sign in zoom')
    email = driver.find_element_by_id('email')
    email.send_keys(EMAIL)
    password = driver.find_element_by_id('password')
    password.send_keys(PWD)
    sign_in = driver.find_element_by_css_selector('#login-form > div:nth-child(4) > div > div.signin > button')
    sign_in.click()
    time.sleep(2)