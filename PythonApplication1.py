"""
from openai import OpenAI

# Initialize the client
client = OpenAI(api_key='')

# Using the updated endpoint
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ]
)

# Output the response
print(response.usage)
"""
"""
import requests
from bs4 import BeautifulSoup

# Step 1: Read the Excel file
file_path = 'C:/Users/u5580340/Desktop/Fourtine.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Step 2: Convert to a list of lists
data = df.values.tolist()

# Step 3: Store only the first 100 rows in the array
array_100_rows = data[:100]

for row in array_100_rows:
    # Join the elements of the row with a comma and space, and print
    print(', '.join(map(str, row)))
 """
import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


#Initialize the client
client = OpenAI(api_key='sk-proj-UsD2piowbm3VJb36xa5NT3BlbkFJlBtasBdYc9dxh8v9Mfyo')


def extract_owner_from_text(text):
    prompt = f"""
    Extract the name of the owner or data controller from the following text:
    
    {text}
    
    Please provide the name in the format: "Owner: [Name]".  and if you don't find it, return I dont Know
    """


# Using the updated endpoint
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts information from text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0
    )

    print(response.usage)
    return response.choices[0].message.content

def scrape_website(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try to find the privacy policy URL
    privacy_policy_url = None
    for link in soup.find_all('a', href=True):
        if 'privacy' in link.text.lower():
            privacy_policy_url = link['href']
            if not privacy_policy_url.startswith('http'):
                privacy_policy_url = requests.compat.urljoin(url, privacy_policy_url)
            break
    
    # Extract text from the main page (About Us, Contact Us)
    about_us_text = ""
    contact_text = ""
    for tag in soup.find_all(['p', 'div']):
        if 'about' in tag.text.lower():
            about_us_text += tag.get_text(separator=" ", strip=True) + " "
        if 'contact' in tag.text.lower():
            contact_text += tag.get_text(separator=" ", strip=True) + " "
    
    # Analyze the extracted text
    owner_info = ""
    if about_us_text:
        owner_info += extract_owner_from_text(about_us_text) + "\n"
    if contact_text:
        owner_info += extract_owner_from_text(contact_text) + "\n"
    
    # Scrape and analyze privacy policy if found
    if privacy_policy_url:
        headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
        response = requests.get(privacy_policy_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        privacy_policy_text = soup.get_text(separator=" ", strip=True)
        owner_info += extract_owner_from_text(privacy_policy_text) + "\n"
    
    return owner_info

# Step 1: Read the Excel file
file_path = 'C:/Users/u5580340/Desktop/Fourtine.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Step 2: Convert to a list of lists
data = df.values.tolist()

# Step 3: Store only the first 100 rows in the array
array_100_rows = data[:100]

for row in array_100_rows:
    # Join the elements of the row with a comma and space, and print
    url = ""
    url = ', '.join(map(str, row))
    owner_info = scrape_website(url)
    print(owner_info)