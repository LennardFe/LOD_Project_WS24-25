import requests
import psycopg2
from dotenv import load_dotenv
import os
import json
from time import sleep
from bs4 import BeautifulSoup

load_dotenv()

API_URL = 'https://mobygames.com/company/'

connection = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
        )
cursor = connection.cursor()

def extract_company_name(html_content):
    """
    Extract all developers' names, IDs, and URLs from the given HTML content.

    :param html_content: HTML string
    :return: List of dictionaries with developer information
    """
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the 'Developers' section specifically
    company_name = soup.find('h1', class_='mb-0').text.strip()

    return company_name

cursor.execute('''SELECT company_id FROM company WHERE company_name is null''')
missing_company_ids = cursor.fetchall()

for id in missing_company_ids:
    response = requests.get(API_URL+str(id[0]))

    # Check if the request was successful
    if response.status_code == 200:
        company_name = extract_company_name(response.text)
        cursor.execute('''UPDATE company SET company_name = %s WHERE company_id = %s''',(company_name, id[0]))
        connection.commit()
        print(f'ID: {id[0]} | Name: {company_name}')

    else:
        print(f"Failed to retrieve the webpage for ID {id[0]}. Status code: {response.status_code}")
connection.close()