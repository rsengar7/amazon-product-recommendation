import os
import json
import gzip
import warnings
import pandas as pd
import openpyxl
import xlrd

merged = pd.read_csv("merged.csv")
print(len(merged))

print(merged.columns)

columns = ['category', 'tech1',
       'fit', 'title', 'also_buy', 'tech2', 'brand', 'feature',
       'also_view', 'main_cat','price',
       'asin', 'imageURL', 'imageURLHighRes',
       'details.Item model number:', 'details.Paperback:',
       'details.Publisher:', 'details.Language:', 'details.ISBN-10:',
       'details.ISBN-13:',
       'details.Electronics:',
       'details.Series:',
       'details.UPC:',
       'details. UNSPSC Code:',
       'overall', 'vote', 'verified',
       'reviewTime', 'style', 'reviewerID','reviewerName', 'reviewText',
       'summary']

merged = merged[columns]

merged.rename(columns={
    "details.Item model number:":"model_number","details. UNSPSC Code:":"unspsc_code",
    "details.ISBN-10:":"isbn_10","details.ISBN-13:":"isbn_13",
                       
}, inplace=True)

merged = merged.drop(columns=["details.Paperback:", "details.Publisher:", "details.Language:", "details.Electronics:",
                 "details.Series:", "details.UPC:"], axis=1)


print()
print(merged.columns)

merged.to_csv("Data/clean_merged.csv")
