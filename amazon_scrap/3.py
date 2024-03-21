import os, sys
import csv
import time
import pandas as pd
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


df = pd.read_csv("amazon_urls.csv")

for index, url in enumerate(df['Urls'].tolist()[0:2000]):
    print(index, "----", len(df))
    base_url = url.split("/ref")[0].replace('dp', 'product-reviews')
    all_review_part = "/ref=cm_cr_arp_d_paging_btm_next_{}?ie=UTF8&reviewerType=all_reviews&pageNumber={}"

    review_url = base_url + all_review_part

    driver.get(review_url)

    for i in range(1, 11):
        # url = "https://www.amazon.com/Scopely-Inc-Stumble-Guys/product-reviews/B0C7WJLQQF/ref=cm_cr_arp_d_paging_btm_next_{}?ie=UTF8&reviewerType=all_reviews&pageNumber={}".format(i, i)
        url = review_url.format(i, i)
        # print(url)
        driver.get(url)

        time.sleep(1)

        for j in range(1, 11):
            ASIN.append(url.split("/")[5])

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
                print("Review Date: ",data.text.split("on")[1].strip())
                Review_date.append(data.text)
            except:
                Review_date.append("")

            try:
                review_xpath = "/html/body/div[1]/div[2]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[{}]/div/div/div[4]/span".format(j)
                data = driver.find_element(by=By.XPATH, value=review_xpath)
                # print("Review : ",data.text)
                Review.append(data.text)
            except:
                Review.append("")
            # print("*"*100)

        # sys.exit()
        # break
    # break

dict1 = {
    "ASIN": ASIN,
    "Names": Names,
    "Review_rating": Review_rating,
    "Review_date": Review_date,
    "Review": Review
}

df = pd.DataFrame(dict1)

# print(df.head())

df.to_csv("amazon_reviews_2000.csv")
