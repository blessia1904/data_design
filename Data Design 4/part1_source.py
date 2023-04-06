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



def part1(header):
    # 1. Using a standard GET request. Read and store the cookies received in the response.  
    URL = "https://www.planespotters.net/user/login"

    session_requests = requests.session()

    first = session_requests.get(URL, headers=header, timeout=10)
    cookies = session_requests.cookies.get_dict()
    print(cookies)

    # 1. In addition, parse the response and read (and store to a string variable) the value of the hidden input field that 
    # will (most likely) be required in the login process.
    soup = BeautifulSoup(first.text, features="lxml")
    hidden = soup.select("div.planespotters-form input[type=hidden]")

    # store the csrf value to a string variable
    hidden = soup.select("div.planespotters-form input[type=hidden]")[0]
    hidden_value = hidden.get("value")
    print(hidden_value)

    
    # store the rid value (since it's not required for login, I didn't use it for POST)
    hidden1 = soup.select("div.planespotters-form input[type=hidden]")[1]
    hidden_value1 = hidden1.get("value")


    # 2. Make a post request using the cookies from (1) as well as all required name-value-pairs
    time.sleep(5)
    second = session_requests.post(URL, 
                            data = {"username" : "uknowwut",
                                    "password" : "1qa2ws3ed",
                                    "csrf": hidden_value},
                            headers = header,
                            cookies=cookies,
                            timeout = 15)

    cookies1 = session_requests.cookies.get_dict()
    print(cookies1)

    # 3. Get the cookies from the response of the post request and add them to your cookies from (1).
    cookies.update(cookies1)


    # 4. Verifies that you are logged in by accessing the profile page with the saved cookies.
    time.sleep(5)
    confirm_URL = "https://www.planespotters.net/user/login"
    page2 = session_requests.get(confirm_URL,
                                    headers=header,  
                                      cookies=cookies)

    doc2 = BeautifulSoup(page2.content, 'html.parser')
    doc2_str = str(doc2)

    if "uknowwut" in doc2_str: # Check whether my username appears on the page.
        print("Success!")
    else:
        print("Failed")

    # 5.Then, print out the following at the end:
    # The entire Jsoup/BeautifulSoup document of your profile page.
    print(doc2)
    # All (combined) cookies from (3).
    print(cookies)
    # A boolean value to show your username is contained in the document in part (5)(a).
    print(bool("uknowwut" in str(doc2.find_all("li", string = 'Personal Gallery'))))



if __name__ == '__main__':
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
    part1(header)

    