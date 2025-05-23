import pandas as pd
import requests
from bs4 import BeautifulSoup
#from openai import OpenAI
from requests.exceptions import RequestException
import re
from urllib.parse import urlparse
from urllib.parse import urljoin
import tldextract
import os
import google.generativeai as genai

counter = 0
counter2 = 0
domain_backUp = ""
# Step 1: Read the Excel file
file_path = 'C:/Users/u5580340/Desktop/tesst.xlsx'  # Replace with your file path
df = pd.read_excel(file_path, header=None)

# Step 2: Convert to a list of lists
data = df.values.tolist()

# Step 3: Store only the first 100 rows in the array
array_100_rows = data[:100]


#Initialize the client
#client = OpenAI(api_key='sk-proj-UsD2piowbm3VJb36xa5NT3BlbkFJlBtasBdYc9dxh8v9Mfyo')
api_key = "AIzaSyCADkdUuS0-za5Q5CbN4pZBOJ6i64znQwQ"
genai.configure(api_key=api_key)


def get_first_half(text):
    mid_index = len(text) // 2
    first_half = text[:mid_index]
    return first_half

def extract_main_domain(url):
    # Extract the main domain
    extracted = tldextract.extract(url)
    
    # Determine if the suffix is a country code
    suffix_parts = extracted.suffix.split('.')
    if len(suffix_parts) > 1 and len(suffix_parts[-1]) == 2:
        # If the last part of the suffix is a two-letter country code, remove it
        main_domain = f"{extracted.domain}.{suffix_parts[-2]}"
    else:
        main_domain = f"{extracted.domain}.{extracted.suffix}"
    
    # Ensure the URL starts with 'https://'
    if not main_domain.startswith(('http://', 'https://')):
        main_domain = 'https://' + main_domain
    
    return main_domain


def get_full_url(base_url, link):
    # Ensure the link is a full URL
    return urljoin(base_url, link)

def extract_owner_from_url(url):
    print("extract_owner_from_url")
    prompt = f"""
        You are an expert in domain owner extraction. 
        ### Instructions:
        1. Identify the name of the data controller or owner from given URL.
        2. If the owner is an abbreviation, PROVIDE the full name.
        3. If the owner is a platform, provide the top-level owner or manager, not sub-entities.
        4. If there is a larger entity or different name associated with the company, also provide this information.

        ### Additional Guidance:
        - Indicate your confidence level in your response. If you are unsure about the information or if it is unclear, please mention that explicitly.
        - Provide the name in the following format: "Owner: [Name]". If applicable, use "BigOwner or another Name: [Name]" for larger entities or different names.
        - Do not include extra text beyond what is necessary for the response and the confidence indication.
        ### Now, please provide the owner information for the following URL:

        Website URL: {url}
"""
###########################################################################    
# Using the updated endpoint
    """  response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts owner of any domain."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0,
    )
    return response.choices[0].message.content
"""
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(prompt)
    return response.candidates[0].content.parts[0].text

########################################################################### 

def extract_owner_from_text(text):
    try:
        print("extract_owner_from_text")
        prompt = f"""
            You are an expert in identifying and extracting ownership information from text. Please extract the name of the owner or data controller from the following text:

            {text}

            ### Instructions:
            1. Provide the name in the format: "Owner: [Name]".
            2. If the text is in a different language, translate the relevant terms to English if possible. Provide the translated name in the format: "Owner: [Translated Name]".
            3. If you are unable to determine the name directly from the text, use the name from the URL and research this owner in your database. If you use this method, mention it clearly.
            4. If there is a larger entity or different name associated with the company, also provide this information in the format: "BigOwner or another Name: [Name]".
            5. Indicate your confidence level in your response. If you are unsure or if the information is not clear, please state your confidence level explicitly. Use terms like "High", "Medium", or "Low".

            ### Example Responses:
            1. **Text**: "La societe est dirigee par Jean Dupont."
                **Response**: Owner: Jean Dupont (Confidence: Medium)

            2. **Text**: "La empresa es propiedad de Grupo Ejemplo."
                **Response**: Owner: Example Group (Confidence: Low)
                BigOwner or another Name: Ejemplo Inc. (Confidence: Low)

            3. **Text**: "The platform is managed by Alpha Ltd."
                **Response**: Owner: Alpha Ltd. (Confidence: High)

            ### Now, please provide the owner information for the following text:

            {text}
        """

        # Using the updated endpoint
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that extracts information from text and provides confidence levels."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # Increased to accommodate extra details
            temperature=0,   # Ensures factual and accurate responses
        )
        return response.choices[0].message.content
        """
        
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            # safety_settings = Adjust safety settings
            # See https://ai.google.dev/gemini-api/docs/safety-settings
        )

        chat_session = model.start_chat(history=[])

        response = chat_session.send_message(prompt)
        return response.candidates[0].content.parts[0].text

    except Exception as e:
        print(f"An error occurred")
        first_half = get_first_half(text)
        return extract_owner_from_text(first_half)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------   
def get_about_us_link(soup, url):
    # Define keywords to search for "About Us" links
    keywords = ['about us', 'about', 'our story', 'who we are']

    # Search for links with the keywords in their text or href attribute
    for keyword in keywords:
        # Search by text
        link = soup.find('a', string=lambda text: text and keyword in text.lower())
        if link:
            about_us_url = get_full_url(url, link['href'])
            return about_us_url

        # Search by href
        link = soup.find('a', href=lambda href: href and keyword in href.lower())
        if link:
            about_us_url = get_full_url(url, link['href'])
            return about_us_url
        

    return None

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
def get_contact_us_link(soup, url):
    # Define keywords to search for "Contact Us" links
    keywords = ['contact us', 'contact', 'get in touch', 'reach us', 'support']

    # Search for links with the keywords in their text or href attribute
    for keyword in keywords:
        # Search by text
        link = soup.find('a', string=lambda text: text and keyword in text.lower())
        if link:
            contact_us_url = get_full_url(url, link['href'])
            return contact_us_url

        # Search by href
        link = soup.find('a', href=lambda href: href and keyword in href.lower())
        if link:
            contact_us_url = get_full_url(url, link['href'])
            return contact_us_url

    return None

#-----------------------------------------------------------------------------------------------------------------------------------------------------------

def get_privacy_policy_link(soup, url):
    # Try to find the privacy policy URL
    # Define keywords to search for
    keywords = ['privacy policy', 'privacy', 'terms of service', 'terms and conditions']
    
    # Search for links with the keywords in their text or href attribute
    for keyword in keywords:
        # Search by text
        
        link = soup.find('a', string=lambda text: text and keyword in text.lower())
        if link:
            privacy_policy_url = get_full_url(url, link['href'])
            return privacy_policy_url
        
         # Search by href
        link = soup.find('a', href=lambda href: href and keyword in href.lower())
        if link:
            privacy_policy_url = get_full_url(url, link['href'])
            return privacy_policy_url        

    return None

#-----------------------------------------------------------------------------------------------------------------------------------------------------------

def scrape_website(response, url):
    #pp-1
    print("---------------------------scrap---------------------------")
    soup = BeautifulSoup(response.content, 'html.parser')
    pp_text = ""
    owner_info = ""
    
    for tag in soup.find_all(['p', 'div']):
        if 'privacy' in tag.text.lower():
           pp_text += tag.get_text(separator=" ", strip=True) + " "
        if 'policy' in tag.text.lower():
           pp_text += tag.get_text(separator=" ", strip=True) + " "
        
# Analyze the extracted text
    if pp_text:
        owner_info += extract_owner_from_text(pp_text) + "\n"
        print(f"from privacy policy text:{owner_info}")
        print("--------------------------------------------------------------------------------")
        
    #pp-2
    pp_url = ""   
    pp_url = get_privacy_policy_link(soup, url)
    print(pp_url)
    print()
    
   # Scrape and analyze privacy policy if found
    if pp_url:
        try:
            response = requests.get(pp_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                privacy_policy_text = soup.get_text(separator=" ", strip=True)
                owner_info += extract_owner_from_text(privacy_policy_text) + "\n"
                print(f"privacy policy link:{owner_info}")
                print("--------------------------------------------------------------------------------")
                
        except RequestException as e:
            print("privacy policy link not reachable")
            print("--------------------------------------------------------------------------------")
            

    # Extract text from the main page (About Us, Contact Us)
    #au+cu-1        
    about_us_text = ""
    contact_text = ""
    for tag in soup.find_all(['p', 'div']):
        if 'about' in tag.text.lower():
            about_us_text += tag.get_text(separator=" ", strip=True) + " "
        if 'contact' in tag.text.lower():
            contact_text += tag.get_text(separator=" ", strip=True) + " "
        
    # Analyze the extracted text

    if about_us_text:
        owner_info += extract_owner_from_text(about_us_text) + "\n"
        print(f"from about us text:{owner_info}")
        print("--------------------------------------------------------------------------------")
    if contact_text:
        owner_info += extract_owner_from_text(contact_text) + "\n"
        print(f"from contact us text:{owner_info}")
        print("--------------------------------------------------------------------------------")
        
    #au+cu-2   
    au_url = get_about_us_link(soup, url)
    if au_url:
        try:
            response = requests.get(au_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                about_us_text = soup.get_text(separator=" ", strip=True)
                owner_info += extract_owner_from_text(about_us_text) + "\n"
                print(f"from about us link:{owner_info}")
                print("--------------------------------------------------------------------------------")
                print()
                
        except RequestException as e:
            print("about us link not reachable")
            print("--------------------------------------------------------------------------------")
            print()
  
    cu_url = get_contact_us_link(soup, url)
    if cu_url:
        try:
            response = requests.get(cu_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                contact_us_text = soup.get_text(separator=" ", strip=True)
                owner_info += extract_owner_from_text(contact_us_text) + "\n"
                print(f"from contact us link:{owner_info}")
                print("--------------------------------------------------------------------------------")
                print()
                
        except RequestException as e:
            print("conact us link not reachable")
            print("--------------------------------------------------------------------------------")
            print()

    footer = soup.find('footer')
    if footer:
        # Extract text from the footer
        footer_text = footer.get_text(separator=' ', strip=True)
        print("Footer Text:")
        owner_info += extract_owner_from_text(footer_text) + "\n"
        print(f"from footer :{owner_info}")
        print("--------------------------------------------------------------------------------")
        print()

    return owner_info
#-----------------------------------------------------------------------------------------------------------------------------------------------------------


for row in array_100_rows:
    # Join the elements of the row with a comma and space, and print
    url = ', '.join(map(str, row))
    print(url)
    print()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)  # Added timeout
    
        # Check the response status
        if response.status_code == 200:
            owner_info = scrape_website(response, url)
            counter += 1
            print(f"Success through web scrap and text analysis{owner_info}")
            print("--------------------------------------------------------------------------------")
                
        else:
            print("Fail 404")
            owner_info = extract_owner_from_url(url)
            print(f"Success through url because couldn't visit website{owner_info}")
            print("--------------------------------------------------------------------------------")
            print()
            
    except RequestException as e:
        domain = ""
        owner_info2 = ""
        counter2 += 1
        
        print(f"Exception{counter2}")
        print(url)
        domain = extract_main_domain(url)
        domain_backUp = domain
        print(f"domain after edit = {domain}")
        
        try:
            response = requests.get(domain, headers=headers, timeout=10)  # Added timeout
            # Check the response status
            if response.status_code == 200:
                owner_info = scrape_website(response, domain)
                counter += 1
                print(f"Success through web scrap and text analysis after extract main domain{owner_info}")
                print("--------------------------------------------------------------------------------")
            else:
                print("Fail 404")
                owner_info = extract_owner_from_url(domain)
                print(f"Success through url because couldn't visit website after extract main domain{owner_info}")
                print("--------------------------------------------------------------------------------")
                
        except RequestException as e:
            print("Exception for extracted domain")
            owner_info = extract_owner_from_url(url)
            print(f"Success through url as it is, sent to GPT{owner_info}")
            print("--------------------------------------------------------------------------------")
    
    print("Give GPT a try")
    owner_info = extract_owner_from_url(url)
    owner_info += extract_owner_from_url(domain_backUp)
    print(f"Success through url and domain as it is, sent to GPT{owner_info}")
    print("--------------------------------------------------------------------------------")
