
from pymongo import MongoClient
import re
from datetime import datetime


def question1and2():
######################### Question 1
    # connect to the MongoDB server running on localhost
    client = MongoClient('localhost', 27017)

    # select the database and collection that contains the Pokemon data
    db = client['samples_pokemon']
    collection = db['samples_pokemon']

    # query the collection to find all Pokemons with candy_count >= 12 (my birthday is Feb.10 so 2+10=12)
    query = {"candy_count": {"$gte": 12}}
    projection = {"name": 1, "_id": 1} 
    # {field: 1 for field in collection.find_one()}  complete version

    # print all names and _ids of matching Pokemons
    for pokemon in collection.find(query, projection):
        print(pokemon)

######################### Question 2
    query2 = {"$or": [{"num": "002"}, {"num": "010"}]}
    projection2 = {"name": 1, "_id": 1}

    for pokemon in collection.find(query2, projection2):
        print(pokemon)



def question3():
    client = MongoClient('localhost', 27017)
    db = client['crunchbase']
    collection = db['crunchbase_database']

    text_regex = re.compile(r"\btext[-\w]*\b")

    # query the collection to find all companies with "text" in their tag_list
    query3 = {"tag_list": {"$regex": text_regex}}
    projection3 = {"_id": 1, "name": 1} # shorter version
    # projection3 = {field: 1 for field in collection.find_one()} # complete version

    # print all names and the _id field of each matching company
    for company in collection.find(query3, projection3):
        print(company)



def question4():
# (i) were founded between 2000 and 2010 (including 2000 and 2010), or (ii) email address is ending in “@gmail.com"
    client = MongoClient('localhost', 27017)
    db = client['crunchbase']
    collection = db['crunchbase_database']


    # Define the start and end dates for the range of years to match
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2010, 12, 31)

    # find email address ends in “@gmail.com” with Regex
    email_regex = re.compile(r'.*@gmail\.com$')
    projection4 = {"name": 1, "twitter_username": 1, "_id": 1, "created_at": 1, "email_address": 1}

    for company in collection.find(projection=projection4):
            created_at_string = company['created_at']
            created_at_datetime = datetime.strptime(created_at_string, "%a %b %d %H:%M:%S UTC %Y")
            if (start_date <= created_at_datetime <= end_date) or (company['email_address'] is not None and email_regex.search(company['email_address'])):
                print("id:", company['_id'], ", company name:", company['name'], ", twitter username:", company['twitter_username'])
                # company['created_at'], company['email_address']




if __name__ == '__main__':
    question1and2()
    question3()
    question4()