# Recommendation System for Amazon Electronics Products

To download the dataset: https://cseweb.ucsd.edu/~jmcauley/datasets.html#amazon_reviews

## Overview:
This repository houses a comprehensive recommendation system for Amazon electronics products. The system encompasses data transformation, pre-processing, machine learning model creation, and a backend system developed using FastAPI and Python. The front end, built with HTML, CSS, and JavaScript, interacts seamlessly with the backend through multiple APIs.

## Table of Contents
1. Data Transformation
2. Pre-processing and Transformation of Data
3. Machine Learning Model Creation
4. Backend System Development
5. Front-end Integration
6. Installation
7. Usage
8. Contributing

## Contents
### 1. Data Transformation
#### 1.1 Transformation of Amazon Electronics Product Data
The Amazon electronics product data, initially in JSON format, is transformed into a data frame using the Pandas library in Python. The process involves reading the JSON file and converting it into a structured data frame for further analysis and manipulation.

Reading the data
```python
def parse(path):
  g = gzip.open(path, 'r')
  for l in g:
    yield json.loads(l)
```

Convert JSON data into dataframe

```python
import pandas as pd
import gzip

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield json.loads(l)

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')
```

### 2. Pre-processing and Transformation of Data:
#### 1. Transformation and Customization of data
To focus the recommendation system on specific product categories, a subset containing only camera and television products is created. This filtering ensures that the model is trained on relevant data for more accurate recommendations.

Custom processing, involving the use of multiple steps:
1. Formatting of words.
2. Stemming of words
3. Remove Punctuation
4. Check NULL Values
5. Features extraction and removal
6. Stopwords removal

#### 2. Save Pre-processed Data to CSV and Load it into DB
The pre-processed data is saved into a CSV file and inserted in the database for backend processing and re-training, allowing for easy access and reuse in subsequent stages of the recommendation system development.
Data pre-processing is essential for cleaning and refining the dataset, ensuring that it is suitable for training machine learning models. These steps contribute to the overall accuracy and effectiveness of the recommendation system.

### 3. Machine Learning Model Creation
#### 3.1 Comparison of different Machine Learning Algorithm for recommendation system 

```python
from surprise import SVD, NMF, NormalPredictor, CoClustering, BaselineOnly, SlopeOne
from surprise import Dataset, Reader
from surprise.model_selection import cross_validate

# Load data from CSV
reader = Reader()
data = Dataset.load_from_df(camera_tv_data[['user_id', 'product_id', 'rating']], reader)

# Compare different models using cross-validation
models = [SVD(), NMF(), NormalPredictor(), CoClustering(), BaselineOnly(), SlopeOne()]

for model in models:
    results = cross_validate(model, data, measures=['RMSE'], cv=5, verbose=True)
    print(f"Model: {model}, RMSE: {results['test_rmse'].mean()}")
```

The Surprise library is employed to create and compare collaborative filtering models. Cross-validation helps evaluate the models based on Root Mean Squared Error (RMSE). Based on the evaluation decided to proceed with SVD Algorithm.

#### 3.2 Model Training and Selection
The selected model (SVD) is trained on the entire dataset, allowing it to learn patterns and relationships for accurate recommendations.

```python
# Train the selected model on the entire dataset
trainset = data.build_full_trainset()
svd_model = SVD()
svd_model.fit(trainset)
```

### 4. Backend System Development
#### 4.1 FastAPI and Python
FastAPI, a modern web framework for building APIs with Python, is chosen for the backend system development. Its asynchronous capabilities and automatic API documentation generation contribute to the efficiency and maintainability of the system.

#### 4.2 Database Setup
A database is designed to store essential information, including user details, product details, recommended products, user selections, and feedback. The database schema is crafted to accommodate the specific data requirements of the recommendation system.

### 5. Front-end Integration
Multiple APIs exposed by the backend system facilitate seamless communication between the front-end template and the recommendation system. The front-end, built using HTML, CSS, and JavaScript, interacts with these APIs to provide users with a responsive and interactive experience.


### 6. Installation
Requirements:

- Python 3.7+
- Pandas
- Surprise
- FastAPI

Instructions:

```python
git clone https://github.com/rsengar7/amazon-product-recommendation.git
cd amazon-product-recommendation
pip install -r requirements.txt
```

### 7. Usage
- Run the Backend:

```python
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

- Access Front-end:
  Open index.html in your browser.

## 8. Contribute

Contributions are always welcome!
Please follow the [contribution guidelines](contributing.md).


