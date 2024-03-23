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
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu') 
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

Names = []
Review_rating = []
Review_date = []
Review = []
ASIN = []
star_rating = []
review_location = []


df = pd.read_csv("amazon_urls.csv")

for index, baseurl in enumerate(df['Urls'].tolist()[0:1]):
    print(index, "----", len(df))
    base_url = baseurl.split("/ref")[0].replace('dp', 'product-reviews')
    all_review_part = "/ref=cm_cr_arp_d_paging_btm_next_{}?ie=UTF8&reviewerType=all_reviews&pageNumber={}"

    stars = {1: 'one_star', 2: 'two_star', 3: 'three_star', 4: 'four_star', 5: 'five_star'}
    for number, star in stars.items():
        all_review_part = "/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar={}&pageNumber={}"
        review_url = base_url + all_review_part
        print(review_url)

        for i in range(1, 6):
            # url = "https://www.amazon.com/Scopely-Inc-Stumble-Guys/product-reviews/B0C7WJLQQF/ref=cm_cr_arp_d_paging_btm_next_{}?ie=UTF8&reviewerType=all_reviews&pageNumber={}".format(i, i)
            url = review_url.format(star, i)
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

dict1 = {
    "ASIN": ASIN,
    "Names": Names,
    "Review_rating": Review_rating,
    "Review_date": Review_date,
    "Rating": star_rating,
    "Review Location": review_location,
    "Review": Review
}

df = pd.DataFrame(dict1)

print(df.head())
df['Review'] = df['Review'].astype(str)
print(len(df))
df = df[df['Review'] != '']
# df = df.replace('', np.nan)
df.dropna(subset = ['Review'], inplace=True)  # Drop rows with missing reviews
print(len(df))
df.to_csv("amazon_reviews_300.csv")
