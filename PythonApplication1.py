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

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import time
from contextlib import contextmanager

@contextmanager
def measure_time(description):
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"{description} took {end_time - start_time:.4f} seconds")
    

#Initialize the client
client = OpenAI(api_key='sk-proj-UsD2piowbm3VJb36xa5NT3BlbkFJlBtasBdYc9dxh8v9Mfyo')


def extract_owner_from_text(text):
    prompt = f"""
    Extract the name of the owner or data controller from the following text:
    
    {text}
    
    Please provide the name in the format: "Owner: [Name]". 
    """


# Using the updated endpoint
    response = client.chat.completions.create(
        model="gpt-4o",
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
   with measure_time("Fetching main page"):    
    response = requests.get(url)
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
   with measure_time("Extracting owner info"):  
    owner_info = ""
    if about_us_text:
        owner_info += extract_owner_from_text(about_us_text) + "\n"
    if contact_text:
        owner_info += extract_owner_from_text(contact_text) + "\n"
    
    # Scrape and analyze privacy policy if found
    if privacy_policy_url:
        response = requests.get(privacy_policy_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        privacy_policy_text = soup.get_text(separator=" ", strip=True)
        owner_info += extract_owner_from_text(privacy_policy_text) + "\n"
    
    return owner_info

# Example usage
url = 'https://www.maannews.net/'
owner_info = scrape_website(url)
print(owner_info)