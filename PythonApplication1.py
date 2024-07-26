import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


counter = 0

# Step 1: Read the Excel file
file_path = 'C:/Users/u5580340/Desktop/Fourtine.xlsx'  # Replace with your file path
df = pd.read_excel(file_path, header=None)

# Step 2: Convert to a list of lists
data = df.values.tolist()

# Step 3: Store only the first 100 rows in the array
array_100_rows = data[:100]

for row in array_100_rows:
    # Join the elements of the row with a comma and space, and print
    url = ', '.join(map(str, row))
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
   
    # Check the response status
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        counter += 1
        print(f"{counter}__")
        print(url)
        print()  
    else:
        counter += 1
        print(f"{counter}-- fail")
        print()