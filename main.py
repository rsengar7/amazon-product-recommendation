# main.py
import hashlib
import json
import time
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import SVD
from collections import defaultdict

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
            sys.exit()
        return conn

# ---------------------------------------------------------------------------------------------------------
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class SignUp(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    country_code: str
    phone_number: str

class Login(BaseModel):
    username: str
    password: str

class ItemRating(BaseModel):
    item_id: str
    rating: int

class UserRating(BaseModel):
    user_id: str
    updated_at: datetime
    user_rating: List[ItemRating]

#----------------------------------------------
def encrypt_password_sha256(password):
    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Convert the password to bytes and update the hash object
    sha256_hash.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    encrypted_password = sha256_hash.hexdigest()

    return encrypted_password

#------------------------------------------------------------------------------------------------------------
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = ["*"]  # Set this to your actual frontend's origin in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/signup")
async def signup_view(request: Request):
    user_data = await request.json()
    data = SignUp(**user_data).dict()

    conn = DBConfig().db_conn()
    cur = conn.cursor()

    # data = signup
    print(data)

    username = data["username"]
    email = data["email"]
    password = data["password"]
    confirm_password = data["confirm_password"]
    country_code = data["country_code"]
    phone_number = data["phone_number"]

    if password != confirm_password:
        return {"response": False, "message": "Password and Confirm Password do not match."}

    encrypted_password = encrypt_password_sha256(password)

    query = "INSERT INTO all_users(username, password, email, country_code, phone_number) VALUES (%s, %s, %s, %s, %s)"
    cur.execute(query, (username, encrypted_password, email, country_code, phone_number))

    # Get the last inserted ID
    inserted_id = cur.lastrowid
    
    return {"success": True, "message":"User SignUp Successful.", "user_id": inserted_id}


@app.post('/user-info')
def user_info(data: dict):
    conn = DBConfig().db_conn()
    cur = conn.cursor()

    # user_id = 3
    user_id = data['user_id']
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    city = data['city']
    country = data['country']
    old_user_id = data['old_user_id']
    gender = data['gender']
    age = data['age']
    native = data['native']
    used = data['used']
    familiar = data['familiar']
    # sponsored_content = data['sponsored_content']
    sponsored_content = ""

    query = """
        INSERT INTO 
            user_info(
                user_id, 
                first_name, 
                last_name, 
                old_user, 
                gender, 
                age, 
                native, 
                familiar, 
                sponsored_content, 
                address, 
                city, 
                country) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    inputs = (user_id, first_name, last_name, old_user_id, gender, age, native, familiar, sponsored_content, address, city, country)
    cur.execute(query, inputs)

    return {"success": True, "message": "Information saved successfully.", "user_id": user_id}


@app.post('/login')
async def login_view(request: Request):
    conn = DBConfig().db_conn()
    cur = conn.cursor()

    user_data = await request.json()
    data = Login(**user_data).dict()

    print(data)

    username = data['username']
    password = data['password']

    encrypted_password = encrypt_password_sha256(password)
    query = "select id from all_users where username = '{}' and password = '{}'".format(username, encrypted_password)
    print(query)
    cur.execute(query)
    res = cur.fetchall()

    if len(res) > 0:
        
        return {"success": True, "message": "login successful", "user_id": res[0][0]}


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
                average_rating,
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


@app.post("/submit-ratings")
def submit_ratings(data: dict):
    conn = DBConfig().db_conn()
    cur = conn.cursor()

    print("*"*100)
    print(data)
    print("*"*100)

    user_id = data["user_id"]
    
    dict1 = {}
    for index, row in enumerate(data["ratings"]):
        index+= 1
        dict1["product"+str(index)] = row

    json_dump = json.dumps(dict1)

    query = "DELETE FROM user_ratings where user_id = '{}'".format(user_id)
    cur.execute(query)

    query = "INSERT INTO user_ratings(user_id, user_rating) VALUES (%s, %s)"
    cur.execute(query, [user_id, json_dump])

    start = time.time()

    out = get_recommendations(user_id, conn)
    print("./"*100)
    print(out)
    print("./"*100)
    print("Toatl Time : -----", int(time.time()) - int(start))

    details = json.dumps(out)

    query = "DELETE FROM user_predicted_products where user_id = '{}'".format(user_id)
    cur.execute(query)

    predicted_product_query = "INSERT INTO user_predicted_products (user_id, product_info) VALUES (%s, %s)"
    cur.execute(predicted_product_query, (user_id, details))

    return {"success": True, "user_id": user_id, "recommended_products": out}


@app.post("/recommended-products")
def display_recommeded_product_view(data: dict):
    conn = DBConfig().db_conn()
    cur = conn.cursor()

    user_id = data['user_id']
    # user_id = 3
    query = "select product_info from user_predicted_products where user_id = {}".format(user_id)
    cur.execute(query)

    data = cur.fetchone()

    products = json.loads(data[0])


    return {"response": True, "data": products}

    
    
import pickle
import numpy as np


# Model Training
def train_with_data(ratings):
    # Define a reader with the rating scale
    reader = Reader(rating_scale=(1, 5))  # Assuming the ratings are from 1 to 5

    # Load the data from the DataFrame into the surprise dataset
    dataset = Dataset.load_from_df(ratings[['reviewerID', 'asin', 'rating']], reader)

    model = SVD()

    model.fit(dataset.build_full_trainset())

    with open('Model/svd_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    return model


# Adding user data into existing dataset for new training
def add_userdata_into_training(user_id, ratings, cur):
    
    cur.execute("select user_rating from user_ratings where user_id = {} limit 1".format(user_id))
    data = cur.fetchall()

    import json

    # Extracting the string from the tuple
    json_string = data[0][0]

    # Load the JSON-like string into a Python dictionary
    data_dict = json.loads(json_string)

    # Convert the dictionary to a Pandas DataFrame
    user_df = pd.DataFrame.from_dict(data_dict, orient='index')
    user_df.rename(columns = {"productId": "asin"}, inplace=True)
    user_df['reviewerID'] = user_id
    ratings_new = pd.concat([user_df, ratings], ignore_index=True)
    # ratings_new = user_df.append(ratings)

    model = train_with_data(ratings_new)
    # model = ""

    return model, ratings_new


def get_top_n(predictions, n=5):
    # Create a dictionary to store recommendations for each user
    top_n = defaultdict(list)

    # Group the predictions by user ID
    for user_id, item_id, true_rating, estimated_rating, _ in predictions:
        top_n[user_id].append((item_id, estimated_rating))
    
    for user_id, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[user_id] = user_ratings[:n]

    return top_n


def get_recommendations(user_id, conn):
    cur = conn.cursor()

    ratings = pd.read_sql_query("select product_id as asin, user_id as reviewerID, rating from product_data", conn)
    # ratings = pd.read_csv("Data/final_data.csv")

    model, df_new_ratings = add_userdata_into_training(user_id, ratings, cur)
    
    # with open('Model/svd_model.pkl', 'rb') as fp:
    #     model = pickle.load(fp)

    test = [(user_id, item_id, actual_rating) for item_id, actual_rating in zip(df_new_ratings['asin'].unique(), df_new_ratings['rating'])]

    predictions = model.test(test)
    
    top_n = get_top_n(predictions, n=20)

    recommended_data = {}
    products = []
    recommendations = top_n[user_id]
    for item_id, rating in recommendations:
        print(f"- Item ID: {item_id}, Estimated Rating: {rating}")
        recommended_data[item_id] = rating
        products.append(item_id)

    query = "Select product_id, product_name, brand, title, features, imageurl_high as image from all_products where product_id IN {} and product_name != '' limit 5".format(tuple(products))
    print("Query : ",query)
    cur.execute(query)

    product_details = cur.fetchall()
    recommended_products = []
    for row in product_details:
        product_row = {}        
        product_row['product_id'] = row[0]
        product_row['rating'] = recommended_data[row[0]]
        product_row['product_name'] = row[1]
        product_row['brand'] = row[2]
        product_row['title'] = row[3]
        # product_row['features'] = row[4]
        
        images = {}
        for index, image in enumerate(row[5].split("|")):
            images[index] = image
        product_row['images'] = images
        recommended_products.append(product_row)


    return recommended_products