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


urls = []
for i in range(1, 331):
    url = "https://www.amazon.com/s?i=mobile-apps&rh=n%3A9209902011&fs=true&page={}&qid=1710971883&ref=sr_pg_2".format(i)

    driver.get(url)
    time.sleep(2)

    for j in range(1, 62):
        try:            
            xpath = "/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[{}]/div/div/span/div/div/div[1]/span/a".format(j)

            data = driver.find_element(by=By.XPATH, value=xpath)

            print(data.get_attribute('href'))
            print("-----------",i)
            urls.append(data.get_attribute('href'))
        except:
            pass

df = pd.DataFrame({"Urls": urls})
print(df.info)

df.to_csv("amazon_urls.csv")
