from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
from pymongo import MongoClient
from collections import Counter
import re
import json
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from fake_useragent import UserAgent


ssense_url = "https://www.ssense.com/en-us/women"

def step_0_selenium():
    s = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=s)
    driver.implicitly_wait(10)
    driver.set_script_timeout(120)
    driver.set_page_load_timeout(10)

    driver.get(ssense_url)
    time.sleep(3)
    sales = driver.find_element(By.CSS_SELECTOR, 'div.plp-sale-filters__wrapper label.plp-sale-filters__label--wrapper')
    sales.click()
    print(driver.current_url)
    time.sleep(5)

    driver.quit()



def step_1_download(header):
# Create a download function to download the first two pages from searching results as HTML files

    def download_file(download_url, header, i):
        response = requests.get(download_url, headers=header, timeout=15)
        html = response.text
        with open(f"ssense_{i}.html", "w") as f:
            f.write(html)


    # for i in range(1,3):
    #     ssense_url = f"https://www.ssense.com/en-us/women/sale?page={i}"
    #     download_file(ssense_url, header, i)
    #     time.sleep(5)



def step_2_getURL():
# Extract the links to each individual product page, 240 URLs in total and download all of them as HTML files

    session = requests.Session()
    retry = Retry(total=3, connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({'User-Agent': UserAgent().random})


    item_url =[]
    file_names = []
    for i in range(1,3):
        file_names.append(f"ssense_{i}.html")

    for i in range(2):
        with open(file_names[i], "r") as f:
            text = f.read()
            soup = BeautifulSoup(text, 'lxml')

        # get each item's url
        content1 = soup.select("div.plp-products__product-tile a")
        for x in content1:
            item_url.append("https://www.ssense.com" + x.get('href'))
    # print(len(item_url))


    def download_file(download_url, i):
        response = session.get(download_url, timeout=15)
        html = response.text
        with open(f"item_{i}_ssense.html", "w") as f:
            f.write(html)

    # for i in range (240):
        # download_file(item_url[i], i)
        # time.sleep(5)
    
    return(file_names)




def step_3_parse(file_names):
# Extract specific elements from HTML files for each women's wear item on sale

    # first get images for each item
    item_image =[]
    for i in range(2):
        with open(file_names[i], "r") as f:
            text = f.read()
            soup = BeautifulSoup(text, 'lxml')

        content0 = soup.select("div.plp-products__product-tile picture.product-tile__image")
        for z in content0:
            outside = z.find('img')['data-srcset']
            item_image.append(''.join(outside))
    # print(item_image)
    # print(len(item_image))


    # get all other information
    file_names3 = []
    for i in range(240):
        file_names3.append(f"item_{i}_ssense.html")

    brand =[]
    original_price =[]
    discount_price =[]
    discounts =[]
    item_sku =[]
    product_title =[]
    item_material =[]
    item_origin =[]
    item_color =[]

    for i in range(240):
        with open(file_names3[i], "r") as f:
            text = f.read()
            soup = BeautifulSoup(text, 'lxml')

            # get each item's original price and convert them to float
        content2 = soup.select("span.product-price__subsection span.product-price__sale-line")
        for a in content2:
            original_price.append(float(a.text.strip().replace('\n', '').replace(' USD', '').replace('$','')))

            # get each item's discount price and convert them to float
        content3 = soup.find_all("span", "product-price__price s-text")
        for b in content3:
            discount_price.append(float(b.text.strip().replace('\n', '').replace(' USD', '').replace('$','')))

        # get each item's percentage off
        content4 = soup.find_all("span", "product-price__price product-price__sale s-text s-text--uppercase")
        for c in content4:
            discounts.append(float(c.text.strip().replace('\n', '').replace('OFF','').replace('%','')))         

        # get each item's brand name
        content5 = soup.select_one("h1.pdp-product-title__brand a")
        for d in content5:
            brand.append(d.text.strip().replace('\n', ''))   

        # get each item's SKU
        content6 = soup.select_one("div.pdp-product-description p[id=pdpProductSKUText]")
        for e in content6:
            item_sku.append(e.text.strip().replace('\n', ''))  
        
        # get each item's title
        content7 = soup.select_one("div.s-row h2.pdp-product-title__name")
        for f in content7:
            product_title.append(f.text.strip().replace('\n', ''))  

        # get each item's materials
        content8 = soup.select_one("div.s-column span p.s-text")
        for g in content8:
            item_material.append(g.text.strip().replace('\n', ''))    

        # get each item's origin     
        content9 = soup.select("div.s-column p.s-text")[3]
        for h in content9:
            item_origin.append(h.text.strip().replace('Made in','').replace('.',''))     

        # get each item's color
        content10 = soup.select("div.s-column p.s-text")[1]
        for h in content10:
            if "color" in h.text or "colo" in h.text:
                item_color.append(h.text.strip().replace('Supplier color:', '').replace('Supplier colo:', '').replace('\t', ''))


    # process discounts again by dividing all numbers by 100
    for y in range(len(discounts)):
        discounts[y] = discounts[y] / 100

    # print(len(item_origin))
    # print(item_origin)

    return(brand, item_image, original_price, discount_price, discounts, item_sku, product_title, item_material, item_origin, item_color)



def step_4_database(brand, item_image, original_price, discount_price, discounts, item_sku, product_title, item_material, item_origin, item_color):
# insert all items'data into MongoDB

    client = MongoClient('localhost', 27017)
    db = client['ssense_database']
    collection = db['ssense']

    # besides the _id auto generated by MongoDB, also make item sku as an index 
    # since sku works as an identifier for each item in retail industry for inventory management
    collection.create_index('item_sku')

    final_ssense_list =[]
    for i in range(240):
        info = {'brand': brand[i], 'original price': original_price[i],'discount price': discount_price[i],
                'discounts': discounts[i],'item title': product_title[i], 'item color': item_color[i], 
                'item material': item_material[i], 'item origin': item_origin[i], 'item image': item_image[i],
                'item sku': item_sku[i]}
        final_ssense_list.append(info)
    # print(len(final_ssense_list))

    collection.insert_many(final_ssense_list)



if __name__ == '__main__':
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
    step_0_selenium()
    step_1_download(header)
    file_names = step_2_getURL()
    brand, item_image, original_price, discount_price, discounts, item_sku, product_title, item_material, item_origin, item_color = step_3_parse(file_names)
    step_4_database(brand, item_image, original_price, discount_price, discounts, item_sku, product_title, item_material, item_origin, item_color)

