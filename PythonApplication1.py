import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from requests.exceptions import RequestException

counter = 0

# Step 1: Read the Excel file
file_path = 'C:/Users/u5580340/Desktop/dataSet.xlsx'  # Replace with your file path
df = pd.read_excel(file_path, header=None)

# Step 2: Convert to a list of lists
data = df.values.tolist()

# Step 3: Store only the first 100 rows in the array
array_100_rows = data[:100]


#Initialize the client
client = OpenAI(api_key='sk-proj-UsD2piowbm3VJb36xa5NT3BlbkFJlBtasBdYc9dxh8v9Mfyo')


def extract_owner_from_url(url):
    prompt = f"""
You are an intelligent assistant. I need you to visit the website provided and find information about the data controller or owner of the website or domain. Please look for any relevant details, such as the name of the data controller, the owner, or any contact information provided for data protection purposes.

Website URL: {url}

 Please provide the name in the format: "Owner: [Name]". You can take afvantage if the name is mentioned in the url it self and you know that it is name of owner.
 please DON'T add extra text, Just follow the format. If the owner was in Abbreviation name, please try to find the full name of that owner.
 """


# Using the updated endpoint
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts information from url."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0
    )
    return response.choices[0].message.content


def extract_owner_from_text(text):
    prompt = f"""
    Extract the name of the owner or data controller from the following text:
    
    {text}
    
    Please provide the name in the format: "Owner: [Name]" and take into consedration different langauges please. if it is in different language 
    try to write the coressponding word in English. Return I don't know if you didn't find the owner name.

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

    #print(response.usage)
    return response.choices[0].message.content

def scrape_website(response):
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
        try:
            response = requests.get(privacy_policy_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                privacy_policy_text = soup.get_text(separator=" ", strip=True)
                owner_info += extract_owner_from_text(privacy_policy_text) + "\n"
            else:
                #print("fail in detecting privacy text")
                owner_info =  extract_owner_from_url(row)
                print(owner_info)
        except RequestException as e:
            #print(f" policy not reachable")
            owner_info =  extract_owner_from_url(row)
            print(owner_info)
            print()
    
    return owner_info


for row in array_100_rows:
    # Join the elements of the row with a comma and space, and print
    url = ', '.join(map(str, row))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)  # Added timeout
    
        # Check the response status
        if response.status_code == 200:
            owner_info = scrape_website(response)
            counter += 1
            if owner_info.strip() == "":
                #print("owner_info is empty")
                owner_info =  extract_owner_from_url(row)
                print(owner_info)
                print()
            else:
                print(owner_info)
                print()
        else:
            counter += 1
            print(f"{counter}")
            owner_info =  extract_owner_from_url(row)
            print(owner_info)
            print()
    except RequestException as e:
        counter += 1
        print(f"{counter}")
        owner_info =  extract_owner_from_url(row)
        print(owner_info)
        print()