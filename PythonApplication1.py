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
    Extract the name of the owner of the website or data controller from the following text:
    
    {text}
    
    Please provide the name in the format: "Owner: [Name]" and take into consedration different langauges please.
    if it is in different language try to write the coressponding word in english 
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
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    owner_info = ""
    owner_info += extract_owner_from_text(soup) + "\n"   
    return owner_info

# Example usage
url = 'https://publictv.in/tamil-nadu-demand-to-release-45-tmc-of-cauvery-water-in-august/'
owner_info = scrape_website(url)
print(owner_info)