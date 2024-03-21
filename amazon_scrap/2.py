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

ASIN = []
Names = []
Ai_Review = []
Ai_tags = []
overall_rating = []
game_price = []
language_supported = []
release_year = []
amazon_listed_date = []
developed_by = []
total_reviews = []
product_description = []
developer_email = []
product_features = []
minimum_operating = []
game_size = []
application_permission = []
Review_contain_url = []

df = pd.read_csv("amazon_urls.csv")
# print(df['Urls'].tolist()[0].split("/")[5])
# sys.exit()

for index, url in enumerate(df['Urls'].tolist()[0:5000]):
    print(index, "----", len(df))
    base_url = url.split("/ref")[0].replace('dp', 'product-reviews')
    all_review_part = "/ref=cm_cr_arp_d_paging_btm_next_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1"

    review_url = base_url + all_review_part

    driver.get(url)

    time.sleep(1)
    ASIN.append(url.split("/")[5])
    Review_contain_url.append(review_url)
    try:
        name_xpath = "/html/body/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[1]/h1/span/span/span/span[2]"
        data = driver.find_element(by=By.XPATH, value=name_xpath)
        Names.append(data.text)
    except:
        Names.append("")

    try:
        ai_review_xpath = "/html/body/div[1]/div[1]/div/div[2]/div[4]/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[1]/p[1]"
        data = driver.find_element(by=By.XPATH, value=ai_review_xpath)
        Ai_Review.append(data.text)
    except:
        Ai_Review.append("")

    try:
        price_xpath = "/html/body/div[1]/div[1]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div/span[2]/strong"
        data = driver.find_element(by=By.XPATH, value=price_xpath)
        game_price.append(data.text)
    except:
        game_price.append("")

    try:
        lan_support_xpath = "/html/body/div[1]/div[1]/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/span[2]"
        data = driver.find_element(by=By.XPATH, value=lan_support_xpath)
        language_supported.append(data.text)
    except:
        language_supported.append("")

    try:
        tag_xpath = "/html/body/div[1]/div[1]/div/div[2]/div[4]/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div"
        data = driver.find_element(by=By.XPATH, value=tag_xpath)
        Ai_tags.append(", ".join(data.text.split("\n")))
    except:
        Ai_tags.append("")

    try:
        overall_rating_xpath = "/html/body/div[1]/div[1]/div/div[2]/div[4]/div/div/div[1]/span[1]/div/div/div/div/div/div[2]/div/div[2]/div/span"
        data = driver.find_element(by=By.XPATH, value=overall_rating_xpath)
        overall_rating.append(data.text.split(" ")[0])
    except:
        overall_rating.append("")

    try:
        game_size_xpath = "/html/body/div[1]/div[1]/div/div[2]/div[2]/div[12]/div[1]/span[2]"
        data = driver.find_element(by=By.XPATH, value=game_size_xpath)
        game_size.append(data.text.split(" ")[0])
    except:
        game_size.append("")

    try:
        minimum_operating_xpath = "/html/body/div[1]/div[1]/div/div[2]/div[2]/div[12]/div[5]/span[2]"
        data = driver.find_element(by=By.XPATH, value=minimum_operating_xpath)
        minimum_operating.append(data.text.split(" ")[0])
    except:
        minimum_operating.append("")

    try:
        application_permission_xpath = "/html/body/div[1]/div[1]/div/div[2]/div[2]/div[12]/ul"
        data = driver.find_element(by=By.XPATH, value=application_permission_xpath)
        application_permission.append(data.text.split(" ")[0])
    except:
        application_permission.append("")

    try:
        developed_by_xpath = "/html/body/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[1]/span/a"
        data = driver.find_element(by=By.XPATH, value=developed_by_xpath)
        developed_by.append(data.text.split(" ")[0])
    except:
        developed_by.append("")


    release = ""
    first_list = ""
    creator = ""
    review_count = ""
    prod_desc = ""
    dev_email = ""
    prod_features = ""
    for i in range(1, 15):
        try:
            developer_email_xpath = "/html/body/div[1]/div[1]/div/div[2]/div[2]/div[{}]".format(i)
            data = driver.find_element(by=By.XPATH, value=developer_email_xpath)
            entry = data.text
            if "Release Date" in entry:
                release = entry.split(":")[1].strip()
            elif "Date first listed on Amazon" in entry:
                first_list = entry.split(":")[1].strip()
            elif "Customer reviews" in entry:
                review_count = entry.split("\n")[1].split(" ")[0]
            elif "Product description" in entry:
                prod_desc = "\n".join(entry.split("\n")[1:])
            elif "Developer info" in entry:
                dev_email = entry.split("\n")[1].strip()
            elif "Product features" in entry:
                prod_features = "\n".join(entry.split("\n")[1:])  
        except:
            pass

    # print(creator)
    print("*"*100)
    if release != "":
        release_year.append(release)
    else:
        release_year.append("")

    if first_list != "":
        amazon_listed_date.append(first_list)
    else:
        amazon_listed_date.append("")

    if review_count != "":
        total_reviews.append(review_count)
    else:
        total_reviews.append("")

    if prod_desc != "":
        product_description.append(prod_desc)
    else:
        product_description.append("")

    if dev_email != "":
        developer_email.append(dev_email)
    else:
        developer_email.append("")

    if prod_features != "":
        product_features.append(prod_features)
    else:
        product_features.append("")


data_dict = {
  "ASIN": ASIN,
  "Names": Names, 
  "total_reviews": total_reviews,
  "overall_rating": overall_rating, 
  "game_price": game_price, 
  "game_size": game_size, 
  "developed_by": developed_by, 
  "developer_email": developer_email, 
  "release_year": release_year, 
  "amazon_listed_date": amazon_listed_date, 
  "language_supported": language_supported, 
  "Ai_Review": Ai_Review, 
  "Ai_tags": Ai_tags, 
  "product_description": product_description, 
  "product_features": product_features, 
  "minimum_operating": minimum_operating, 
  "application_permission": application_permission,
  "reviews_url": Review_contain_url
}

df = pd.DataFrame(data_dict)

print(df.head())

df.to_csv("amazon_games_info_5000.csv")
