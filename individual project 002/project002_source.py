from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
from pymongo import MongoClient
import pymongo
import re
import json
import http.client, urllib.parse
from urllib.parse import urlencode




# Question1:
ape_url = "https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold"


def Question2(header):

    # create a download function first
    def download_file(driver, i):
        html = driver.page_source
        with open(f"bayc_{i}.html", "w") as f:
            f.write(html)


# write code that uses Selenium to access the URL from (1)
    s = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=s)
    driver.implicitly_wait(10)
    driver.set_script_timeout(120)
    driver.set_page_load_timeout(10)
    driver.get(ape_url)

# click on each of the top-8 most expensive Bored Apes
# store the resulting details page to disk, “bayc_[N].html”

    for i in range(0,8):
        all = driver.find_elements(By.XPATH, "//div[@class='sc-29427738-0 sc-e7851b23-1 dVNeWL hfa-DJE Asset--loaded']")
        time.sleep(4)
        all[i].click()
        time.sleep(4)
        # download_file(driver, i) # here I downloaded the ape's html
        time.sleep(3)
        driver.back()
        time.sleep(4)
    driver.quit()



def Question3():

    file_names = []
    for i in range(8):
        file_names.append(f"bayc_{i}.html")

    ape_names =[]
    all_attributes =[]
    background = []
    clothes =[]
    earring =[]
    eyes =[]
    fur =[]
    hat =[]
    mouth =[]

# Write code that goes through all 8 html files downloaded in (2) and 
# stores each ape’s name (its number) and all its attributes in a document inside a MongoDB collection called “bayc”

    for i in range(8):
        with open(file_names[i], "r") as f:
            text = f.read()
            soup = BeautifulSoup(text, 'lxml')

        # get apes' names
        attribute2 = soup.find_all("h1", "sc-29427738-0 hKCSVX item--title")
        for attr2 in attribute2:
            ape_names.append(attr2.text)

        # get apes' attributes
        attribute1 = soup.find_all("div", "sc-d6dd8af3-0 hkmmpQ item--property")

        if len(attribute1) == 7:
            for attr1 in attribute1:
                all_attributes.append(f"Ape{i}:"+ attr1.text)
        else:
            for n in range(7):
                if n < len(attribute1):
                    attr = attribute1[n].text
                else:
                    attr="NA"
                all_attributes.append(f"Ape{i}:{attr}")
    # print(len(all_attributes)) # 8 apes, each should have 7 attributes (if no then NA), so 56 in total

    for qq in all_attributes:
        if 'Background' in qq:
            color = re.search(r'(?<=Background)[A-Za-z ]+', qq).group().strip()
            background.append(color)


    for i, qq in enumerate(all_attributes):
        if 'Clothes' in qq:
            clo = re.search(r'(?<=Clothes)[A-Za-z ]+', qq).group().strip()
            clothes.append(clo)
    clothes.insert(5, 'NA')

    for qq in all_attributes:
        if 'Earring' in qq:
            ear = re.search(r'(?<=Earring)[A-Za-z ]+', qq).group().strip()
            earring.append(ear)
    earring.insert(1, 'NA') # there'r 4 apes don't have earrings
    earring.insert(2, 'NA')
    earring.insert(4, 'NA')  
    earring.insert(7, 'NA')  

    for qq in all_attributes:
        if 'Eyes' in qq:
            eye = re.search(r'(?<=Eyes)[A-Za-z ]+', qq).group().strip()
            eyes.append(eye)


    for qq in all_attributes:
        if 'Fur' in qq:
            furr = re.search(r'(?<=Fur)[A-Za-z ]+', qq).group().strip()
            fur.append(furr)

    for qq in all_attributes:
        if 'Hat' in qq:
            hatt = re.search(r'(?<=Hat)[A-Za-z ]+', qq).group().strip()
            hat.append(hatt)

    for qq in all_attributes:
        if 'Mouth' in qq:
            mouthh = re.search(r'(?<=Mouth)[A-Za-z ]+', qq).group().strip()
            mouth.append(mouthh)

    # insert all apes'date into MongoDB
    client = MongoClient('localhost', 27017)
    db = client['bayc_database']
    collection = db['bayc']

    final_ape_list =[]
    for i in range(8):
        info = {'name': ape_names[i], 'background': background[i],'clothes': clothes[i],'earring': earring[i],'eyes': eyes[i], 'fur': fur[i], 'hat': hat[i], 'mouth': mouth[i]}
        final_ape_list.append(info)
    # print(len(final_ape_list))

    collection.insert_many(final_ape_list)


def Question4(header):
# Yellow Pages uses GET requests for its search. Write a program that searches on yellowpages.com for the top 30 “Pizzeria” in San Francisco 
# Save each search result page to disk, “sf_pizzeria_search_page.html”

    yp_url = "https://www.yellowpages.com/search?"
    keyword = {"search_terms": "pizzeria", "geo_location_terms": "San Francisco, CA"}
    yp_url += urlencode(keyword)
    # print(yp_url)

    def download_file(download_url, header):
        response = requests.get(download_url, headers=header, timeout=10)
        html = response.content
        with open(f"sf_pizzeria_search_page.html", "wb") as f:
            f.write(html)

    # download_file(yp_url, header)


def Question5():
# write code that opens the search result page saved in (4) and parses out all shop information 
# (search rank, name, linked URL [this store’s YP URL], star rating If It Exists, number of reviews IIE, 
# TripAdvisor rating IIE, number of TA reviews IIE, “$” signs IIE, years in business IIE, review IIE, and amenities IIE).  
# Please be sure to skip all “Ad” results.

    with open("sf_pizzeria_search_page.html", "r") as f:
        text = f.read()
        soup = BeautifulSoup(text, features="lxml")
        all_stores = soup.select("div.v-card")
    # print(all_stores)
    # print(len(all_stores)) # there are 33 total resturants in the html file

    rank_and_name = []
    linked_url = []
    star_ratings =[]
    star_rating =[] # updated one
    reviews_count = []
    TA_rating_and_reviewcount =[]
    dollar_sign =[]
    year =[]
    review =[]
    amenities =[]
    # each information list should contain 30 elements, etiher NA or legit info

    for i in range(1,31): # the first one and the last two are ads, so I excluded them
        a = all_stores[i]

        # rank, name
        for b in a.select("h2.n"):
            rank_and_name.append(b.text)

        # linked URL
        for c in a.select("h2.n a"):
            linked_url.append("https://www.yellowpages.com" + c.get('href'))
        
        # star rating If It Exists
        if len(a.select("div.ratings div.result-rating")) == 1:
            for d in a.select("div.ratings div.result-rating"):
                outside = d.get('class')
                star_ratings.append(''.join(outside))
        elif len(a.select("div.ratings div.result-rating")) == 0:
            star_ratings.append("NA")
        
        # number of reviews IIE
        if len(a.select("a.rating span.count")) == 1:
            for e in a.select("a.rating span.count"):
                reviews_count.append(e.text)
        elif len(a.select("a.rating span.count")) == 0:
            reviews_count.append("NA")

        # TripAdvisor rating IIE, number of TA reviews IIE
        if len(a.select("div.ratings")) ==1:
            for f in a.select("div.ratings"):
                ta = f.get('data-tripadvisor')
                if ta is None:
                    TA_rating_and_reviewcount.append("NA")
                else:
                    TA_rating_and_reviewcount.append(ta)

        # “$” signs IIE
        if len(a.select("div.price-range")) ==1:
            for g in a.select("div.price-range"):
                if g.text == '':
                    dollar_sign.append("NA")
                else:
                    dollar_sign.append(g.text)
        elif len(a.select("div.price-range"))==0:
            dollar_sign.append("NA")

        # years in business IIE
        if len(a.select("div.years-in-business div.number")) ==1:
            for h in a.select("div.years-in-business div.number"):
                if h.text == '':
                    year.append("NA")
                else:
                    year.append(h.text)
        elif len(a.select("div.years-in-business")) ==0:
            year.append("NA")

        # review IIE
        if len(a.select("div.snippet p.with-avatar")) ==1:
            for j in a.select("div.snippet p.with-avatar"):
                if j.text == '':
                    review.append("NA")
                else:
                    review.append(j.text)
        elif len(a.select("div.snippet p.with-avatar")) == 0:
            review.append("NA")

        # amenities
        if len(a.select("div.amenities-info span")) != 0:
            amen_list =[]
            for k in a.select("div.amenities-info span"):
                if k.text == '':
                    amenities.append("NA")
                else:
                    amen_list.append(k.text)
            amenities.append(amen_list)
        elif len(a.select("div.amenities-info span")) == 0:
            amenities.append("NA")


    # update star ratings
    for z in star_ratings: # trying to get rid of "result-rating" here
        if 'result-rating' in z:
            star_rating.append(z.replace('result-rating', ''))
        else:
            star_rating.append(z)

    # print(rank_and_name)
    # print(len(review)) 
    # so far every info list contains 30 elements for 30 pizzerias
    return(rank_and_name, linked_url, star_rating, reviews_count, TA_rating_and_reviewcount, dollar_sign, year, review, amenities)


def Question6(rank_and_name, linked_url, star_rating, reviews_count, TA_rating_and_reviewcount, dollar_sign, year, review, amenities):
# Copy your code from (5). Modify the code to create a MongoDB collection called “sf_pizzerias” that 
# stores all the extracted shop information, one document for each shop.

    # modify my code from (5) so that ranks and names are separate
    ranks =[]
    names =[]
    for l in rank_and_name:
        rank, name = l.split(". ", 1)
        ranks.append(int(rank))
        names.append(name)

    # modify my code from (5) so that TripAdvisor's ratings and reviews are separate
    TA_rating =[]
    TA_reviewcount =[]
    for m in TA_rating_and_reviewcount:
        if m != "NA":
            content = json.loads(m)
            TA_rating.append(content["rating"])
            TA_reviewcount.append(content["count"])
        else: 
            TA_rating.append("None")
            TA_reviewcount.append("None")

    # organize all info list into each corresponding pizzeria
    restaurant_list = []
    for aa,bb,cc,dd,ee,ff,gg,hh,jj,kk,ll in zip(ranks, names, linked_url, star_rating, reviews_count, TA_rating, TA_reviewcount, dollar_sign, year, review, amenities):
        restaurant_dict = {
        'ranks':aa,
        'names': bb,
        'url': cc,
        'star rating': dd,
        'reviews count': ee,
        'TA rating': ff,
        'TA review count': gg,
        'dollar': hh,
        'year in bus': jj,
        'review': kk,
        'amenities': ll
    }
        restaurant_list.append(restaurant_dict)
    # print(restaurant_list)

    # insert all pizzerias' info to MongoDB
    client = MongoClient('localhost', 27017)
    db = client["sf_pizzerias_database"]
    collection = db["sf_pizzerias"]

    for restaurant in restaurant_list:
        collection.insert_one(restaurant)

    # double check to see if I have correctly inserted 30 pizzerias
    count = collection.count_documents({})
    print(count) # yes, got 30



def Question7(header):
# Write code that reads all URLs stored in “sf_pizzerias” and download each shop page.  
# Store the page to disk, “sf_pizzerias_[SR].html” (replace [SR] with the search rank).

    client = MongoClient('localhost', 27017)
    db = client['sf_pizzerias_database']
    collection = db['sf_pizzerias']

    # get all documents in the collection
    documents = collection.find({})
    # get all URLs
    all_url = []
    for each in documents:
        all_url.append(each["url"])


    def download_file(download_url, header, i):
        response = requests.get(download_url, headers=header, timeout=15)
        html = response.text
        with open(f"sf_pizzerias_{i}.html", "w") as f:
            f.write(html)

    # download all 30 html files here for pizzerias
    # for i in range (0,30):
    #     download_file(all_url[i], header, i)
    #     time.sleep(5)



def Question8():
# Write code that reads the 30 shop pages saved in (7) and parses each shop’s address, phone number, and website.
    file_names = []
    for i in range(30):
        file_names.append(f"sf_pizzerias_{i}.html")
    # print(file_names)

    addresses = []
    phone_numbers = []
    websites = []
    for i in range(30):
        with open(file_names[i], "r") as f:
            text = f.read()
            soup = BeautifulSoup(text, 'lxml')
            # parses each shop’s address
            content1 = soup.select("a.directions span.address")
            for x in content1:
                location = x.text
                addresses.append(location)
            # parses each shop’s phone number
            content2 = soup.select("a.phone")
            for y in content2:
                phone = y.text
                phone_numbers.append(phone)
            # parses each shop’s websites
            content3 = soup.select("a.website-link")
            if len(content3) == 1:
                for w in content3:
                    external = w.get('href')
                    websites.append(external)
            elif len(content3) == 0:
                websites.append("NA")

    # print(phone_numbers)
    # print(len(phone_numbers))

    return(addresses, phone_numbers, websites)


def Question9(addresses, phone_numbers, websites):
# Copy your code from (8).  Modify the code to query each shop address’ geolocation (long, lat).  

    # clean up addresses so that I can get separate geo info (especially street and zip code) in an easier way
    updated_addresses =[]
    for u in addresses:
        updated_addresses.append(re.sub(r'san francisco, CA', '', u, flags=re.IGNORECASE))

    # only getting these two info because it's sure that all pizzerias are in city SF and country US
    street = []
    zip_code =[]
    for q in updated_addresses:
        parts = q.rsplit(' ', 1)
        street.append(parts[0])
        zip_code.append(parts[1])

    geo=[]
    conn = http.client.HTTPConnection('api.positionstack.com')
    for i in range(30):
        params = urllib.parse.urlencode({
            'access_key': '8f5817d53ee4a90685dba194f8c895fd',
            'query': street[i],
            'region': 'San Francisco',
            'postal_code': zip_code[i],
            'country': 'US',
            'limit': 1
        })
        conn.request('GET', '/v1/forward?{}'.format(params))
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        geo.append(json.loads(data))
    # print(geo)

    # get only latitude and longitude values here
    geolocation=[]
    for o in geo:
        lat = o['data']
        lat01 = lat[0]
        lat02 = lat01['latitude']
        lon = o['data']
        lon01 = lon[0]
        lon02 = lon01['longitude']
        geolocation.append({'latitude': lat02, 'longitude': lon02})
    # print(geolocation)
    # print(len(geolocation))


# Update each shop document on the MongoDB collection “sf_pizzerias” to 
# contain the shop’s address, phone number, website, and geolocation.

    client = MongoClient('localhost', 27017)
    db = client['sf_pizzerias_database']
    collection = db['sf_pizzerias']

    for i in range(30):
        query = {'ranks': i+1}
        update = {'$set': {'address': addresses[i],'phone number': phone_numbers[i],'website': websites[i],'geolocation': geolocation[i]}}
        collection.update_one(query, update)



if __name__ == '__main__':
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
    Question2(header)
    Question3()
    Question4(header)
    rank_and_name, linked_url, star_rating, reviews_count, TA_rating_and_reviewcount, dollar_sign, year, review, amenities = Question5()
    Question6(rank_and_name, linked_url, star_rating, reviews_count, TA_rating_and_reviewcount, dollar_sign, year, review, amenities)
    Question7(header)
    addresses, phone_numbers, websites = Question8()
    Question9(addresses, phone_numbers, websites)
