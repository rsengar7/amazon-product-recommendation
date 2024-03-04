from flask import Flask, request, jsonify
import hashlib
import json
import pickle
import pandas as pd
import time
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import SVD
from collections import defaultdict
from mysql.connector import connect, Error as MySQLConnectionError
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)

# Configure CORS
CORS(app)


# Database Configuration Class
class DBConfig:
    """
    This class encapsulates the database configuration and provides a method to connect to the database.
    It uses the mysql.connector library to establish a connection using the provided credentials.
    """
    def __init__(self):
        self.host = "localhost"
        self.port = 3306
        self.database = "recommendation_backup"
        self.user = "python"
        self.password = "Qwerty@1"

    def db_conn(self):
        """
        Establishes a connection to the MySQL database and returns the connection object.
        Raises an exception if the connection fails.
        """
        try:
            conn = connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                autocommit=True
            )
            return conn
        except MySQLConnectionError as err:
            print(f"Database connection failed: {err}")
            raise

# Password Encryption Function
def encrypt_password_sha256(password):
    """
    Encrypts a password using SHA-256 hashing algorithm.
    This ensures that passwords are stored securely in the database.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password.encode('utf-8'))
    return sha256_hash.hexdigest()

# Root Endpoint
@app.route('/')
def root():
    """
    The root endpoint of the application.
    It returns a simple JSON message as a way to check that the application is running.
    """
    return jsonify({"message": "Hello World"})

# User Signup Endpoint
@app.route('/signup', methods=['POST'])
def signup_view():
    """
    The signup endpoint allows new users to create an account.
    It expects a JSON payload with username, email, password, etc.
    The password is encrypted before storing it in the database.
    """
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    country_code = data.get("country_code")
    phone_number = data.get("phone_number")

    if password != confirm_password:
        return jsonify({"response": False, "message": "Passwords do not match."}), 400

    password_encrypted = encrypt_password_sha256(password)

    try:
        conn = DBConfig().db_conn()
        cur = conn.cursor()
        query = ("INSERT INTO all_users (username, password, email, country_code, phone_number) "
                 "VALUES (%s, %s, %s, %s, %s)")
        cur.execute(query, (username, password_encrypted, email, country_code, phone_number))
        inserted_id = cur.lastrowid
        return jsonify({"success": True, "message": "User SignUp Successful.", "user_id": inserted_id}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()

# User Login Endpoint
@app.route('/login', methods=['POST'])
def login_view():
    """
    The login endpoint authenticates users based on their username and password.
    The password is encrypted and compared against the stored password in the database.
    If authentication is successful, it returns the user's ID.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    password_encrypted = encrypt_password_sha256(password)

    try:
        conn = DBConfig().db_conn()
        cur = conn.cursor()
        query = "SELECT id FROM all_users WHERE username = %s AND password = %s"
        cur.execute(query, (username, password_encrypted))
        user = cur.fetchone()

        if user:
            return jsonify({"success": True, "message": "Login successful", "user_id": user[0]}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()

# Display Products Endpoint
@app.route('/display-product', methods=['GET'])
def display_product_view():
    """
    The display product endpoint fetches a list of products from the database.
    It formats the product data, including splitting image URLs, and returns it as JSON.
    """
    try:
        conn = DBConfig().db_conn()
        cur = conn.cursor(dictionary=True)
        query = ("SELECT product_id, category, product_name, brand, average_rating, "
                 "imageurl_high as imageurl FROM all_products LIMIT 100")
        cur.execute(query)
        products = cur.fetchall()

        product_list = []
        for product in products:
            product_dict = {
                "id": product['product_id'],
                "category": product['category'],
                "name": product['product_name'],
                "brand": product['brand'],
                "average_rating": product['average_rating'],
                "imageurl": {f"image{i+1}": url for i, url in enumerate(product['imageurl'].split('|'))}
            }
            product_list.append(product_dict)

        return jsonify({"response": "true", "data": product_list}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()

# User Info Update
@app.route('/user-info', methods=['POST'])
def user_info():
    """
    The user info endpoint allows updating user-specific information in the database.
    It expects a JSON payload with user details such as first name, last name, address, etc.
    The data is then inserted into the `user_info` table for the specified user.
    """
    data = request.json
    user_id = data.get('user_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    address = data.get('address')
    city = data.get('city')
    country = data.get('country')
    old_user_id = data.get('old_user_id', '')
    gender = data.get('gender', '')
    age = data.get('age', '')
    native = data.get('native', '')
    used = data.get('used', '')
    familiar = data.get('familiar', '')
    sponsored_content = ''

    try:
        conn = DBConfig().db_conn()
        cur = conn.cursor()
        query = ("INSERT INTO user_info (user_id, first_name, last_name, old_user, gender, age, native, "
                 "familiar, sponsored_content, address, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        cur.execute(query, (user_id, first_name, last_name, old_user_id, gender, age, native, familiar,
                            sponsored_content, address, city, country))
        return jsonify({"success": True, "message": "Information saved successfully.", "user_id": user_id}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()

# Submit Ratings
@app.route('/submit-ratings', methods=['POST'])
def submit_ratings():
    """
    The submit ratings endpoint allows users to submit their ratings for products.
    It expects a JSON payload with the user ID and a list of ratings for different products.
    The ratings are stored in the database, and any previous ratings by the user are overwritten.
    This endpoint could be extended to trigger recommendation updates based on new ratings.
    """
    data = request.json
    user_id = data.get('user_id')

    ratings_dict = {f"product{index+1}": rating for index, rating in enumerate(data.get('ratings', []))}
    ratings_json = json.dumps(ratings_dict)

    try:
        conn = DBConfig().db_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_ratings WHERE user_id = %s", (user_id,))
        cur.execute("INSERT INTO user_ratings (user_id, user_rating) VALUES (%s, %s)", (user_id, ratings_json))

        details = json.dumps(
            get_recommendations(user_id, conn)
        )

        query = "DELETE FROM user_predicted_products where user_id = '{}'".format(user_id)
        cur.execute(query)

        predicted_product_query = "INSERT INTO user_predicted_products (user_id, product_info) VALUES (%s, %s)"
        cur.execute(predicted_product_query, (user_id, details))

        return jsonify({"success": True, "user_id": user_id}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()


# Display Recommended Products
@app.route('/recommended-products', methods=['POST'])
def display_recommended_product_view():
    """
    The display recommended products endpoint fetches personalized product recommendations for a user.
    It expects a JSON payload with the user ID and returns a list of recommended products.
    The recommendations should be previously generated and stored in the database.
    """
    data = request.json
    user_id = data.get('user_id')

    try:
        conn = DBConfig().db_conn()
        cur = conn.cursor()
        cur.execute("SELECT product_info FROM user_predicted_products WHERE user_id = %s", (user_id,))
        product_info = cur.fetchone()

        if product_info:
            products = json.loads(product_info[0])
            return jsonify({"response": True, "data": products}), 200
        else:
            return jsonify({"response": False, "message": "No recommendations found for the user."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()

from flask import request, jsonify
import json

@app.route('/submit-selection', methods=['POST'])
def submit_selection():
    """
    Endpoint to record a user's product selection based on recommendations.

    Expects a JSON payload containing:
    - user_id: The ID of the user making the selection.
    - selected_product: The index of the selected product in the user's recommended products list.

    The function retrieves the user's recommended products from the database,
    identifies the selected product by its index, and stores the selection in the `user_choice` table.

    Returns a JSON response indicating the success or failure of the operation.
    """
    try:
        # Extract data from the incoming request
        data = request.json
        user_id = data.get('user_id')
        selected_product_index = int(data.get('selected_product'))

        # Establish a database connection
        conn = DBConfig().db_conn()
        cur = conn.cursor()

        # Retrieve the user's recommended products from the database
        cur.execute("SELECT product_info FROM user_predicted_products WHERE user_id = %s", (user_id,))
        product_info = cur.fetchone()

        if product_info:
            # Parse the JSON data to get the list of recommended products
            products = json.loads(product_info[0])

            # Extract the selected product's ID using the provided index
            if selected_product_index < len(products):
                selected_product_id = products[selected_product_index]['product_id']

                # Insert the user's selection into the `user_choice` table
                query = "INSERT INTO user_choice (user_id, product_info) VALUES (%s, %s);"
                cur.execute(query, (user_id, selected_product_id))
            else:
                return jsonify({"response": False, "error": "Selected product index out of range"}), 400

        # Commit the transaction and close the cursor
        conn.commit()

        # Return a success response
        return jsonify({"response": True}), 200
    except Exception as e:
        # Log the exception and return an error response
        print(f"An error occurred while submitting the selection: {e}")
        return jsonify({"response": False, "error": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route('/login-timetrack', methods=['POST'])
def login_timetrack():
    """
    Logs the time each user accesses a specific page.
    
    Expects a JSON payload with 'user_id', 'timer_value', and 'pageName'.
    - 'user_id' should be an integer identifying the user.
    - 'timer_value' could represent the time spent or a timestamp.
    - 'pageName' is the name of the accessed page, which is parsed to remove any file extensions.
    
    The function inserts this data into the 'timetrack' table in the database.
    
    Returns a JSON response indicating success or failure of the logging operation.
    """
    # Attempt to extract and process the data from the incoming JSON payload
    try:
        data = request.json
        timetracking = (
            data.get('user_id'),  # Extract user_id
            data.get('timer_value'),  # Extract timer_value
            data.get('pageName').split(".")[0],  # Extract and parse pageName
        )

        # SQL query to insert the timetracking data into the database
        query = "INSERT INTO timetrack (user_id, timer_value, pagename) VALUES (%s, %s, %s);"

        # Establish a database connection and execute the query
        conn = DBConfig().db_conn()
        cur = conn.cursor()
        cur.execute(query, timetracking)
        conn.commit()  # Commit the transaction

        # Return a success response
        return jsonify({"response": True}), 200

    except KeyError as e:
        # Handle missing data in the JSON payload
        print(f"Missing data in the request: {e}")
        return jsonify({"response": False, "error": f"Missing data: {e}"}), 400

    except Error as e:
        # Handle database errors
        print(f"Database error: {e}")
        return jsonify({"response": False, "error": "Database error"}), 500

    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}")
        return jsonify({"response": False, "error": "An unexpected error occurred"}), 500

    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route('/submit-feedback', methods=['POST'])
def feedback_view():
    """
    The submit feedback endpoint allows users to submit feedback on their experience.
    It expects a JSON payload with the user ID and feedback scores for various aspects (e.g., satisfaction levels).
    The feedback is saved to the database, which could be used for quality assurance and service improvement.
    
    Returns:
    - JSON response indicating the success or failure of the feedback submission.
    """
    data = request.json

    # Extract feedback details from the request
    time_details = (
        data.get('user_id'),
        data.get('well_chosen'),
        data.get('satisfied'),
        data.get('good_recommend'),
        data.get('recommend_align'),
        data.get('recommend_manipulate'),
        data.get('recommend_pushed_item')
    )

    query = """
        INSERT INTO user_feedback (user_id, well_chosen, satisfied, good_recommend, 
                                   recommend_align, recommend_manipulate, recommend_pushed_item)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    
    try:
        # Establish a new database connection
        conn = DBConfig().db_conn()
        cur = conn.cursor()

        # Execute the query with the feedback details
        cur.execute(query, feedback_details)
        
        # Commit the changes to the database
        conn.commit()

        # Return a success response
        return jsonify({"response": True, "message": "Feedback submitted successfully."}), 200
    except Exception as e:
        # Log the exception and return a failure response
        print(f"An error occurred while submitting feedback: {e}")
        return jsonify({"response": False, "error": str(e)}), 500
    finally:
        # Ensure that the database cursor and connection are closed
        if cur:
            cur.close()
        if conn:
            conn.close()



def train_with_data(ratings):
    """
    Trains an SVD model using provided ratings data and handles exceptions related to the training process.
    
    Parameters:
    - ratings: DataFrame with columns ['reviewerID', 'asin', 'rating'] representing user IDs, item IDs, and ratings.
    
    Returns:
    - Trained SVD model or None if an exception occurs during training.
    """
    try:
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(ratings[['reviewerID', 'asin', 'rating']], reader)
        model = SVD()
        model.fit(data.build_full_trainset())
        
        with open('Model/svd_model.pkl', 'wb') as f:
            pickle.dump(model, f)
        
        return model
    except Exception as e:
        print(f"An error occurred during model training: {e}")
        return None


def add_userdata_into_training(user_id, ratings, cur):
    """
    Incorporates user-specific ratings into the existing ratings dataset, retrains the model, and handles exceptions.
    
    Parameters:
    - user_id: ID of the user whose ratings are to be added.
    - ratings: Existing ratings DataFrame.
    - cur: Database cursor object.
    
    Returns:
    - Tuple containing the retrained model and the updated DataFrame. Returns (None, None) if an exception occurs.
    """
    try:
        cur.execute("SELECT user_rating FROM user_ratings WHERE user_id = %s LIMIT 1", (user_id,))
        data = cur.fetchall()
        user_ratings = json.loads(data[0][0])
        # Convert the dictionary to a Pandas DataFrame
        user_df = pd.DataFrame.from_dict(user_ratings, orient='index')
        user_df.rename(columns = {"productId": "asin"}, inplace=True)
        user_df['reviewerID'] = user_id
        ratings_combined = pd.concat([user_df, ratings], ignore_index=True)
        model = train_with_data(ratings_combined)
        return model, ratings_combined
    except Exception as e:
        print(f"An error occurred while adding user data into training: {e}")
        return None, None


def get_top_n(predictions, n=5):
    """
    Retrieves the top-N recommendations for each user from a set of predictions, with error handling.
    
    Parameters:
    - predictions: List of predictions from the SVD model.
    - n: Number of top recommendations to return.
    
    Returns:
    - Dictionary with user IDs as keys and lists of top-N (item ID, estimated rating) tuples as values.
      Returns an empty dictionary if an error occurs.
    """
    try:
        top_n = defaultdict(list)
        for uid, iid, _, est, _ in predictions:
            top_n[uid].append((iid, est))
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]
        return top_n
    except Exception as e:
        print(f"An error occurred in generating top-N recommendations: {e}")
        return {}


def get_recommendations(user_id, conn):
    """
    Generates and fetches product recommendations for a given user, handling any exceptions that occur.
    
    Parameters:
    - user_id: ID of the user for whom recommendations are generated.
    - conn: Active database connection object.
    
    Returns:
    - List of recommended product details. Returns an empty list if an error occurs.
    """
    try:
        cur = conn.cursor()
        ratings_query = "SELECT product_id AS asin, user_id AS reviewerID, rating FROM product_data"
        ratings = pd.read_sql_query(ratings_query, conn)
        model, updated_ratings = add_userdata_into_training(user_id, ratings, cur)
        if model is None:
            raise ValueError("Model training failed.")
        testset = [(user_id, item_id, actual_rating) for item_id, actual_rating in zip(updated_ratings['asin'].unique(), updated_ratings['rating'])]

        predictions = model.test(testset)
        top_n = get_top_n(predictions, n=20)

        recommended_data = {}
        products = []
        recommendations = top_n[user_id]
        for item_id, rating in recommendations:
            print(f"- Item ID: {item_id}, Estimated Rating: {rating}")
            recommended_data[item_id] = rating
            products.append(item_id)

        query = "Select product_id, product_name, price, brand, title, features, imageurl_high as image from all_products where product_id IN {} and product_name != '' and price != '00' limit 5".format(tuple(products))
        cur.execute(query)

        product_details = cur.fetchall()
        recommended_products = []
        for row in product_details:
            product_row = {}        
            product_row['product_id'] = row[0]
            product_row['rating'] = recommended_data[row[0]]
            product_row['product_name'] = row[1]
            product_row['price'] = row[2].split("\n")[0]
            product_row['brand'] = row[3]
            product_row['title'] = row[4]
            # product_row['features'] = row[4]
            
            images = {}
            for index, image in enumerate(row[6].split("|")):
                images[index] = image
            product_row['images'] = images
            recommended_products.append(product_row)
        
        return recommended_products
    except Exception as e:
        print(f"An error occurred in generating recommendations: {e}")
        return []


if __name__ == '__main__':
    app.run(debug=True)  # Turn off debug mode in production environments
