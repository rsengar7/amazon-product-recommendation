import os, sys
import csv
import time
import pandas as pd
import numpy as np
import requests as re
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu') 
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

Names = []
name_url = []
user_id = []
Review_rating = []
Review_date = []
Review = []
ASIN = []
star_rating = []
review_location = []


df = pd.read_csv("amazon_urls.csv")

upper_limit = 14000
lower_limit = 15000

for index, baseurl in enumerate(df['Urls'].tolist()[upper_limit:lower_limit]):
    print(index, "----", lower_limit)
    base_url = baseurl.split("/ref")[0].replace('dp', 'product-reviews')
    all_review_part = "/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar={}&pageNumber={}"

    review_url = base_url + all_review_part
    url2 = review_url.format('one_star', 1)
    try:
        driver.get(url2)
        rate1 = ""

        try:
            total_xpath = "/html/body/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/div[1]/div[3]/span"
            data = driver.find_element(by=By.XPATH, value=total_xpath)
            print("Check Rate: ",data.text)
            rate1 = int(data.text.split(" ")[0].replace(",",""))
        except Exception as ex:
            print(ex)
            pass
        
        if rate1 == 0:
            stars = {1: 'one_star'}
        else:
            stars = {1: 'one_star', 2: 'two_star', 3: 'three_star', 4: 'four_star', 5: 'five_star'}


        stars = {1: 'one_star', 2: 'two_star', 3: 'three_star', 4: 'four_star', 5: 'five_star'}
        for number, star in stars.items():
            all_review_part = "/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar={}&pageNumber={}"
            review_url = base_url + all_review_part
            # print(review_url)
            page_num = 11
            rate = 0
            review_number = 6
            try:
                url1 = review_url.format(star, 1)
                driver.get(url1)
                rate = ""
                review_number = 6

                try:
                    total_xpath = "/html/body/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/div[1]/div[3]/span"
                    data = driver.find_element(by=By.XPATH, value=total_xpath)
                    print("User Name : ",data.text)
                    rate = int(data.text.split(" ")[0].replace(",",""))
                except:
                    pass

                try:
                    review_number_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div[1]/div[4]/div[2]"
                    data = driver.find_element(by=By.XPATH, value=review_number_xpath)
                    print("Review Number : ",data.text)
                    review_number = int(data.text.split(",")[1].strip().split(" ")[0])
                    print("review_number : ",review_number)
                except:
                    pass
            except:
                pass

            if rate == 0:
                page_num = 1
            elif review_number in list(range(0, 10)):
                page_num = 2
            elif review_number in list(range(10, 20)):
                page_num = 3
            elif review_number in list(range(20, 30)):
                page_num = 4
            elif rate in list(range(1, 10)):
                page_num = 2
            elif rate in list(range(10, 20)):
                page_num = 3
            elif rate in list(range(20, 30)):
                page_num = 4
            elif rate in list(range(30, 40)):
                page_num = 5
            elif rate in list(range(40, 50)):
                page_num = 6
            elif rate in list(range(50, 60)):
                page_num = 7
            elif rate in list(range(60, 70)):
                page_num = 8
            elif rate in list(range(70, 80)):
                page_num = 9
            else:
                pass


            for i in range(1, page_num):
                # url = "https://www.amazon.com/Scopely-Inc-Stumble-Guys/product-reviews/B0C7WJLQQF/ref=cm_cr_arp_d_paging_btm_next_{}?ie=UTF8&reviewerType=all_reviews&pageNumber={}".format(i, i)
                url = review_url.format(star, i)
                try:
                    driver.get(url)
                    time.sleep(1)

                    for j in range(1, 11):
                        # time.sleep(1)

                        try:
                            profile_name_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[{}]/div/div/div[1]/a/div[2]/span".format(j)
                            data = driver.find_element(by=By.XPATH, value=profile_name_xpath)
                            # print("User Name : ",data.text)
                            Names.append(data.text)
                        except:
                            Names.append("")

                        try:
                            rate_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[{}]/div/div/div[2]/a".format(j)
                            data = driver.find_element(by=By.XPATH, value=rate_xpath)
                            # print("Summarized Review : ",data.text)
                            Review_rating.append(data.text)                            
                        except:
                            Review_rating.append("")

                        try:
                            profile_link_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[{}]/div/div/div[1]/a".format(j)
                            data = driver.find_element(by=By.XPATH, value=profile_link_xpath)
                            # print("Summarized Review : ",data.text)
                            user_link = data.get_attribute('href')
                            name_url.append(user_link)
                            user_id.append(user_link.split("account.")[1].split("/")[0])
                            print("User Id : ",user_link.split("account.")[1].split("/")[0])
                            # print("Url : ", name_url)
                        except:
                            name_url.append("")
                            user_id.append("")

                        try:
                            review_date_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[{}]/div/div/span".format(j)
                            data = driver.find_element(by=By.XPATH, value=review_date_xpath)
                            row = data.text.split("the")[1]
                            print("Review Date: ",row.split("on")[1].strip())
                            print("Review Location: ",row.split("on")[0].strip())
                            Review_date.append(row.split("on")[1].strip())
                            review_location.append(row.split("on")[0].strip())
                        except:
                            Review_date.append("")
                            review_location.append("")

                        try:
                            review_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[{}]/div/div/div[4]/span".format(j)
                            data = driver.find_element(by=By.XPATH, value=review_xpath)
                            # print("Review : ",data.text)
                            Review.append(data.text)
                        except:
                            Review.append("")

                        if Names[-1] == "" and Review_rating[-1] == "" and Review_date[-1] == "" and review_location[-1] == "" and Review[-1] == "":
                            ASIN.append("")
                            star_rating.append("")
                        else:
                            ASIN.append(url.split("/")[5])
                            star_rating.append(number)
                            
                        # print("*"*100)
                except:
                    pass
    except:
        pass
dict1 = {
    "ASIN": ASIN,
    "User_id": user_id,
    "Names": Names,
    "Review_rating": Review_rating,
    "Review_date": Review_date,
    "Rating": star_rating,
    "Review Location": review_location,
    "Review": Review,
    "User_url": name_url
}

# print(dict1)
print(len(Names))
print(len(name_url))
print(len(Review_rating))
print(len(Review_date))
print(len(Review))
print(len(ASIN))
print(len(star_rating))
print(len(review_location))


df = pd.DataFrame(dict1)

print(df.head())
df['Review'] = df['Review'].astype(str)
print(len(df))
df = df[df['Review'] != '']
# df = df.replace('', np.nan)
df.dropna(subset = ['Review'], inplace=True)  # Drop rows with missing reviews
print(len(df))
df.to_csv("amazon_reviews_15000.csv")
