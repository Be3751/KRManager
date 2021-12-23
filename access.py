from selenium import webdriver
import time
from private_val import EMAIL, PWD

root = 'http://localhost:8080/notify/'
target = root + 'auth'
goal = root + 'auth/complete'
driver = webdriver.Safari()
driver.get(target)

if not driver.current_url == target:
    print('sign in zoom')
    email = driver.find_element_by_id('email')
    email.send_keys(EMAIL)
    password = driver.find_element_by_id('password')
    password.send_keys(PWD)
    sign_in = driver.find_element_by_css_selector('#login-form > div:nth-child(4) > div > div.signin > button')
    sign_in.click()
    time.sleep(2)

while True:
    if driver.current_url == goal or driver.current_url == root:
        print(f'current url is {driver.current_url}.')
        print('quit the driver.')
        driver.quit()
        break