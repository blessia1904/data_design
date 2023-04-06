from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import time
import re
import numpy as np

# a) use the URL identified above and write code that loads eBay's search result page containing sold "amazon gift card". 
# Save the result to file. Give the file the filename "amazon_gift_card_01.html".

def download_file(download_url, header, i): # create a download function
    response = requests.get(download_url, headers=header, timeout=10)
    html = response.text
    with open(f"amazon_gift_card_{i}.html", "w") as f:
        f.write(html)

def problem_1a(header):
    url="https://www.ebay.com/sch/i.html?_fsrp=1&rt=nc&_from=R40&_nkw=amazon+gift+card&_sacat=0&LH_Sold=1"
    download_file(url, header, "01")


# b) take your code in (a) and write a loop that will download the first 10 pages of search results. 
# Save each of these pages to "amazon_gift_card_XX.html" (XX = page number).

def problem_1b(header):
    link=[]
    for a in range (2,11):
        website= str("https://www.ebay.com/sch/i.html?_fsrp=1&rt=nc&_from=R40&_nkw=amazon+gift+card&_sacat=0&LH_Sold=1&_pgn=") + str(a)
        link.append(website)
    print(link) # get rest of 9 pages' URLs
    
    for i in range (9): # use the function to download rest 9 html 
        download_file(link[i], header, f"{i+2:02}")
        time.sleep(10) # 10 seconds pause


# c) write code that loops through the pages you downloaded in (b), opens and parses them to a Python or Java xxxxsoup-object.

def problem_1c():
    file_names = []
    for b in range(10):
        file_names.append(f"amazon_gift_card_{b+1:02}.html")
    # print(file_names)

    soup_body=[]
    for c in range(10):
        with open(file_names[c], "r") as f:
            text = f.read()
            soup = BeautifulSoup(text, features="lxml")
            soup_body.append(soup)
    return(soup_body)


# d) using your code in (c) and your answer to 1 (g), identify and print to screen the title, price, and shipping price of each item.
    
def problem_1d(soup_body):
    item_list = []
    title=[]
    price=[]
    shipping=[]

    for d in range(10):
        list_of_contents = soup_body[d].select("div.s-item__wrapper") # get the whole info box on each page
        item_list += list_of_contents[1:] # there should be 60 items/boxes on each page, 600 items in total (the 1st one is a line so exclude it here)
    
    for e in item_list:
        if len(e.select('div.s-item__title span')) > 1: # noticed there are some lists contain 2 elements, titles are stored as the 1st one
            title.append(e.select('div.s-item__title span')[0].text)
        else:
            title.append(e.select('div.s-item__title span')[0].text)
    for f in range(600):
        if "New Listing" in title[f]: # remove "New Listing" from titles
            title[f] = title[f].replace('New Listing', '')
            print(title[f])
        else:
            print(title[f])
    print(len(title))

    for g in item_list:
        for h in g.select('span.s-item__price'):
            price.append(h.text)
    print(price)
    print(len(price))

    for j in item_list:
        if len(j.select("div.s-item__detail span.s-item__shipping")) == 0:
            shipping.append("Free shipping") # there are several items have no shipping values, so I treated them as Free shipping
        else:
            shipping.append(j.select("div.s-item__detail span.s-item__shipping")[0].text)   
    print(shipping)
    print(len(shipping))

    return(title, price, shipping)



# e) using RegEx, identify and print to screen gift cards that sold above face value. e., use RegEx to extract 
# the value of a gift card from its title when possible (doesn’t need to work on all titles, > 90% success rate is sufficient). 
# Next compare a gift card’s value to its price + shipping (free shipping should be treated as 0).  
# If value < price + shipping, then a gift card sells above face value.

def problem_1ef(title, price, shipping):
    confusing_title =[]
    for x in range(600):
        title[x] = re.findall(r"\d*\.?\d+", str(title[x]))
        if len(title[x]) > 1 :
            confusing_title.append(title[x])
        if len(title[x]) == 2:
            title[x] = title[x][0] # went thru the cases when length==2, the true value is usually the 1st element
            title[x] = float(title[x])
        elif len(title[x]) > 2 or len(title[x]) == 0:
            title[x] = 0 # when length>3, it's hard to get a true value, most of them have price ranges so would ignore them anayway
        elif len(title[x]) == 1:
            title[x] = float(title[x][0])
    print(title)
    print(len(title))
    # print(len(confusing_title)) # there'r 50 titles that have more than 1 value, even if ignore all of them, success rate = 92%

    
    for y in range(600):
        if 'to' in price[y]: # some titles have price ranges, ignore them
            price[y] = 0
        else:
            price[y] = re.findall(r"\d+\.\d+", str(price[y]))
            price[y] = float(price[y][0])
    print(price)
    print(len(price))

    for z in range(600):
        if shipping[z] == "Free shipping":
            shipping[z] = 0
        else:
            shipping[z] = re.findall(r"\d+\.\d+", str(shipping[z]))
            shipping[z] = float(shipping[z][0])
    print(shipping)
    print(len(shipping))

    # So far each of 600 items has its own corresponding title, price, and shipping, so I can directly add or subtract them

    count =[]
    for q in range(600):
        if title[q] == 0 or price[q] == 0:
            continue
        else:
            above_face = np.subtract(np.add(price[q],shipping[q]), np.array(title[q]))
        if above_face > 0:
            count += "1"
            print(f"The gift card's title price is: " + str(title[q]), 
            "listing price is: " + str(price[q]), 
            "shipping fee is: " + str(shipping[q]))
    print("The total amount of gift cards that sells above face value: " + str(len(count)))



# f) What fraction of Amazon gift cards sells above face value? Why do you think this is the case?

    fraction = len(count)/600
    print(fraction) # the fraction is 39%

    # There might be several reasons contributing this kind of case:
    # 1. Sellers want to make profits, such as by overcharging shipping fees. 
    # I noticed that some shipping fees were more than $10, $20 and even $60.
    # 2. Sellers want to cover all expenses associated with (or caused by) this gift card, 
    # such as ebay selling fee, transportation fee, etc.. So the price or shipping fee would be elevated.
    # 3. How we dealt with numbers in the dataset. Some items had no shipping information, and we treated them as free shipping. 
    # Some listing prices had ranges, so we ignored them - treated them as 0. Not all of the numbers from titles were extracted accurately. 
    # And these could lead to discrepancies.  



# PART 2
# a) Following the steps we discussed in class and write code that automatically logs into the website fctables.com

def problem_2():
    
    URL = "https://www.fctables.com/"
    time.sleep(5)

    #An open session carries the cookies and allows you to make post requests
    session_requests = requests.session()

    res = session_requests.post(URL,
                            data = {"login_username" : "uknowwut", # my username
                                    "login_password" : "1qa2ws3ed", # my password
                                    "user_remeber" : "1",
                                    "login_action" : "1"},
                            headers = dict(referer = "https://www.fctables.com/"),
                            timeout = 15)
    
    # This will get us the Cookies.
    cookies = session_requests.cookies.get_dict()
    print(cookies)
    
    # b. Verify that you have successfully logged in by checking whether the word “Wolfsburg” appears on the page.

    bet_URL = "https://www.fctables.com/tipster/my_bets/"
    
    page2 = session_requests.get(bet_URL,  
                                    cookies=cookies)
    
    doc2 = BeautifulSoup(page2.content, 'html.parser')
    doc2_str = str(doc2)
    # print(doc2_str)

    if "Wolfsburg" in doc2_str: # Check whether the word “Wolfsburg” appears on the page.
        print("Success!")
    else:
        print("Failed")

    




if __name__ == "__main__":
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
    # problem_1a(header)
    # problem_1b(header)
    # soup_body = problem_1c()
    # title, price, shipping = problem_1d(soup_body)
    # problem_1ef(title, price, shipping)
    problem_2()

