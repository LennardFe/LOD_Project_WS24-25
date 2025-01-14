import requests
import psycopg2
from dotenv import load_dotenv
import os
import json
from time import sleep
from bs4 import BeautifulSoup
import re

SLEEP_DURATION = 0.1
API_URL = 'https://mobygames.com/game/'
FETCH_LIMIT = 1000

def extract_company_ids(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')


    # Find the 'Developers' section specifically
    developers_dt = soup.find('dt', string='Developers')
    developer_ids = set()

    if developers_dt:
        # Find the developer links in the next <dd> element
        developers_dd = developers_dt.find_next_sibling('dd')

        if developers_dd:
            # Find all developer links
            developer_links = developers_dd.find_all('a', href=re.compile(r'/company/\d+/'))

            for developer_link in developer_links:
                match = re.search(r'/company/(\d+)/', developer_link.get('href', ''))
                developer_id = match.group(1) if match else None
                developer_ids.add(developer_id)

    # Find the 'Publishers' section
    publishers_dt = soup.find('dt', string='Publishers')
    publisher_ids = set()
    if publishers_dt:
        # Find the developer links in the next <dd> element
        publishers_dd = publishers_dt.find_next_sibling('dd')

        if publishers_dd:
                # Find all developer links
            publisher_links = publishers_dd.find_all('a', href=re.compile(r'/company/\d+/'))

            for publisher_link in publisher_links:
                match = re.search(r'/company/(\d+)/', publisher_link.get('href', ''))
                publisher_id = match.group(1) if match else None
                publisher_ids.add(publisher_id)

    return [developer_ids, publisher_ids]

def parse_html_from_url(url):
    """
    Parse HTML from a given URL.

    :param url: URL of the webpage
    :return: Extracted game information
    """
    # Send a request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        return extract_company_ids(response.text)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

def main():
    load_dotenv()

    connection = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )
    cursor = connection.cursor()
    cursor.execute('''SELECT MAX(game_id) FROM games_companies''')
    last_game_id = cursor.fetchone()[0]
    cursor.execute('''SELECT game_id FROM game WHERE game_id > %s ORDER BY game_id  LIMIT %s''', (last_game_id,FETCH_LIMIT))
    game_ids = cursor.fetchall()


    for id in game_ids:
        company_ids = parse_html_from_url(API_URL+str(id[0]))
        for developer_id in company_ids[0]:
            cursor.execute('''INSERT INTO company (company_id) VALUES (%s) ON CONFLICT DO NOTHING''', (developer_id,))
            cursor.execute('''INSERT INTO games_companies (game_id, company_id, type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING''', (id[0], developer_id, 'developer'))
        for publisher_id in company_ids[1]:
            cursor.execute('''INSERT INTO company (company_id) VALUES (%s) ON CONFLICT DO NOTHING''', (publisher_id,))
            cursor.execute('''INSERT INTO games_companies (game_id, company_id, type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING''', (id[0], publisher_id, 'publisher'))
        connection.commit()
        print(id[0])
        sleep(SLEEP_DURATION)
    connection.close()


# Allows the script to be imported without running main()
if __name__ == '__main__':
    main()