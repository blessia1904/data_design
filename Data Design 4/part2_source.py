from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import time
import re
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
from http.cookiejar import CookieJar



def part2a():
    # driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
    s = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=s)
    driver.implicitly_wait(10)
    driver.set_script_timeout(120)
    driver.set_page_load_timeout(10)

# navigates to google.com, and searches for "askew" as well as "google in 1998"
    driver.get("https://google.com/")
    inp = driver.find_element("css selector", "input[type=text]")
    time.sleep(3)
    inp.send_keys("askew\n")
    # driver.save_screenshot('askew screenshot.png')
    time.sleep(5)

    driver.get("https://google.com/")
    inp = driver.find_element("css selector", "input[type=text]")
    time.sleep(2)
    inp.send_keys("google in 1998\n")
    time.sleep(5)
    driver.quit()


def part2b(header):
    # driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
    s = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=s)
    driver.implicitly_wait(10)
    driver.set_script_timeout(120)
    driver.set_page_load_timeout(10)

# write a script that goes to bestbuy.com, clicks on Deal of the Day
    URL2 = "https://www.bestbuy.com/"
    driver.get(URL2)
    deal = driver.find_element(By.LINK_TEXT, 'Deal of the Day')
    deal.click()
    time.sleep(4)

# reads how much time is left for the Deal of the Day and prints the remaining time to screen
    source = driver.page_source
    # print(source)
    soup = BeautifulSoup(source, 'html.parser')
    remain_time = soup.select("div.countdown-clock")
    # print(time)
    print(remain_time[0].text)

# clicks on the Deal of the Day (the actual product), clicks on its reviews
    product = driver.find_element(By.CSS_SELECTOR, 'div.wf-offer-content a.wf-offer-link')
    product.click()
    time.sleep(3)
    reviews = driver.find_element(By.CSS_SELECTOR, 'div.c-ratings-reviews span.c-reviews')
    reviews.click()
    time.sleep(6)
    product_url = driver.current_url

    driver.quit()

# saves the resulting HTML to your local hard drive 
    def download_file(download_url, header): # create a download function
        response = requests.get(download_url, headers=header, timeout=10)
        html = response.text
        with open(f"bestbuy_deal_of_the_day.html", "w") as f:
            f.write(html)
    
    download_file(product_url, header)

    

if __name__ == '__main__':
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
    part2a()
    part2b(header)