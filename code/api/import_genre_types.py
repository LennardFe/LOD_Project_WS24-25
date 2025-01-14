import requests
import psycopg2
from dotenv import load_dotenv
import os
import json
from time import sleep

load_dotenv()

API_URL = 'https://api.mobygames.com/v1/genres'


connection = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
        )
cursor = connection.cursor()

params={'api_key':os.getenv("API_KEY")}
response = requests.get(url=API_URL, params=params)
genre_data = response.json()

seen_ids = set()

# Gehe durch die erhaltenen Genres und füge nicht-gesehene IDs ein
for genre in genre_data['genres']:
    genre_id = genre['genre_category_id']
    genre_name = genre['genre_category']

    if genre_id not in seen_ids:
        cursor.execute('''INSERT INTO genre_type (genre_type_id, name) VALUES (%s, %s)''', (genre_id, genre_name))
        seen_ids.add(genre_id)

connection.commit()
connection.close()