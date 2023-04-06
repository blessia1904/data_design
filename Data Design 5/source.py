import warnings
import requests
import json
import codecs
from bs4 import BeautifulSoup
import mysql.connector
import pymysql


URL = "https://api.github.com/repos/apache/hadoop/contributors"

def question2(header):
# This is the Apache Hadoop Github Repo's contributors’ endpoint. 
# Extract the JSON corresponding to the first 100 contributors from this API. 

    params = {"per_page": 100}
    page = requests.get(URL, headers=header,params=params, timeout=10)
    
    contributor=[]
    if page.status_code == 200: # Check if the response was successful, then parse the JSON response content
        contributors = page.json()
    # Login names of the first 100 contributors
        for i in contributors:
            contributor.append(i["login"])
        # print(len(contributor))
        print("The first 100 contyyributors are:" + str(contributor))
    return contributors


def question3(header,contributors):
# For each of the 100 contributors extracted in (2), write code that accesses their user information and 
# extracts "login", "id", "location", "email", "hireable", "bio", "twitter_username", "public_repos", "public_gists", 
# "followers", "following", "created_at" (and print those to screen)

    # Get each contributor's user information thru their urls
    users = []
    for i in range(0,100):
        user_url = contributors[i]["url"]
        user_page = requests.get(user_url, headers=header)
        if user_page.status_code == 200: 
            user_data = user_page.json()
            users.append(user_data)
    # print(users)

    user_information_list =[]
    key_info = ["login","id","location","email","hireable","bio","twitter_username","public_repos","public_gists","followers","following","created_at"]
    # extract information we need
    for i in range(0,100):
        user_information ={}
        for key in key_info:
            user_information[key] = users[i][key]
        user_information_list.append(user_information)
    for each_user_info in user_information_list:
        print(each_user_info)

    return(user_information_list)
    


#ignore warnings
warnings.filterwarnings("ignore")
SQL_DB = "ucdavis"

def question4(user_information_list):
# Write code that creates an SQL database + table, and stores all the information obtained in (3) in it.  

    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=" ", # deleted my password here :)
        database="ucdavis"
    )
    cursor = conn.cursor()

    # Create a table to store the data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contributors (
        id INT PRIMARY KEY,
        login VARCHAR(255),
        location VARCHAR(255),
        email VARCHAR(255),
        hireable BOOL, 
        bio TEXT,
        twitter_username VARCHAR(255),
        public_repos INT,
        public_gists INT,
        followers INT,
        following INT,
        created_at VARCHAR(255)
    )
    """)

    # Insert the data into the table
    for contributor in user_information_list:
        cursor.execute("""
        INSERT INTO contributors (
            id, login, location, email, hireable, bio, twitter_username,
            public_repos, public_gists, followers, following, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            contributor["id"], contributor["login"], contributor["location"], contributor["email"],
            contributor["hireable"], contributor["bio"], contributor["twitter_username"],
            contributor["public_repos"], contributor["public_gists"], contributor["followers"],
            contributor["following"], contributor["created_at"]
        ))

    select_sql = "SELECT * FROM contributors"
    cursor.execute(select_sql)
    rows = cursor.fetchall()
    for row in rows:
        print(row)


# Please be cautious of the data type you choose for each collumn and briefly justify your decisions.  
    # I chose datatype INT for ID, public_repos, public_gists, followers, and following because they are all composed of whole numbers.
    # I chose datatype VAR(255) for login, location, email, twitter_username, and created_at because it can store up to 255 characters,
    # which is suitable, efficient, and enough for those five info (since they are all short to medium-length strings).
    # I chose datatype BOOL for hireblae because it is True or False (0 or 1), and in MySQL it's the alias of tinyint(1).
    # I chose datatype TEXT for bio because some people are writing long sentences, 
    # which makes TEXT a good choice for storing very long strings as I don't know the length of the string in advance.

# What do you choose as Primary Key and why?
    # I chose ID as the primary key because it can uniquely identify each contributor in the table.



# 5. Optimize your code in (4) to allow for quick look-ups of "login", "location", and "hireable".
    cursor.execute("CREATE INDEX login_index ON contributors (login)")
    cursor.execute("CREATE INDEX location_index ON contributors (location)")
    cursor.execute("CREATE INDEX hireable_index ON contributors (hireable)")

# What choices do you make and why?
    # I created index for these three features because an index stores a sorted copy of the data 
    # in one or more columns of a table, along with a pointer to the corresponding rows in the table. 
    # By creating an index on a column, the database system can look up the values in that column more quickly and efficiently.

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()



if __name__ == '__main__':
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Authorization": 'token ' + 'please insert your token'}
    contributors = question2(header)
    user_information_list = question3(header, contributors)
    question4(user_information_list)

