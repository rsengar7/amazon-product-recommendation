# main.py

'''
Database Connection and Configuration for REST API
'''
try:
    # Necessary Imports
    import os, sys
    import mysql.connector as mysqldb

    # from app.controller.serviceProvider import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_USER, DB_PORT
    
    print("All the Modules are Successfully Imported")
except Exception as e:
    # PLEASE IMPORT THE MODULES FIRST
    print("Enable to import all the necessary Modules---", e)
    sys.exit()


class DBConfig():
    ''' 
    Database Initialization
    '''
    def __init__(self):
        self.mysqldb = mysqldb

    def __str__(self):
        return self.__class__.__name__

    def db_conn(self):
        ''' DataBase Connection '''
        try:
            conn = self.mysqldb.connect(
                host="localhost", 
                port=3306, 
                database="recommendation", 
                user="python", 
                password="Qwerty@1", 
                autocommit=True
            )    # Local
        except Exception as err:
            print(err)
        return conn
# ---------------------------------------------------------------------------------------------------------
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class SignUp(BaseModel):
    first_name: str
    last_name: str
    email: str
    country_code: str
    phone_number: str

class ItemRating(BaseModel):
    item_id: str
    rating: int

class UserRating(BaseModel):
    user_id: str
    updated_at: datetime
    user_rating: List[ItemRating]
#------------------------------------------------------------------------------------------------------------
import pandas as pd
from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/signup")
def signup_view(signup: SignUp):
    conn = DBConfig().db_conn()
    cur = conn.cursor()

    data = signup.dict()
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    country_code = data["country_code"]
    phone_number = data["phone_number"]

    query = "INSERT INTO all_users(first_name, last_name, email, country_code, phone_number) VALUES (%s, %s, %s, %s, %s)"
    cur.execute(query, (first_name, last_name, email, country_code, phone_number))

    return {"response": "true", "message":"User SignUp Successful."}


@app.get("/display-product")
def display_product_view():
    conn = DBConfig().db_conn()
    cur = conn.cursor()

    df = pd.read_sql_query("""
            select 
                product_id, 
                category, 
                product_name,
                brand,
                average_rating
                imageurl_high as imageurl
            from 
                all_products 
            limit 100""", 
        conn
    )

    product_li = []
    for row in df.values.tolist():
        dict1 = {}
        dict1["id"] = row[0]
        dict1["category"] = row[1]
        dict1["name"] = row[2]
        dict1["brand"] = row[3]
        dict1["average_rating"] = row[4]
        
        image_dict = {}
        for index, url in enumerate(row[5].split("|")):
            index = index + 1
            image_dict["image"+str(index)] = url

        dict1["imageurl"] = image_dict
        product_li.append(dict1)
    
    return {"response": "true", "data": product_li}

@app.post("/user-rating")
def user_rating(userrating: UserRating):
    conn = DBConfig().db_conn()
    cur = conn.cursor()

    data = userrating.dict()
    print(data)

    user_id = data["user_id"]
    dict1 = {}
    for index, row in enumerate(data["user_rating"]):
        index+= 1
        dict1["product"+str(index)] = row

    json_dump = json.dumps(dict1)

    query = "INSERT INTO user_ratings(user_id, user_rating) VALUES (%s, %s)"
    cur.execute(query, [user_id, json_dump])

    # Transfer the capture data to the machine learning model to predict the 5 recommended products
    return {"response":"true", "message": "response saved successfully."}

