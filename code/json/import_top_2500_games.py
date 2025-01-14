import psycopg2
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

connection = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
        )
cursor = connection.cursor()

f = open('../../data/Top2500GamesbyRating.json')
games_json = json.load(f)

for game in games_json:
    if re.search(r'^[12]\d{3}$', game['release_date']):
        game['release_date'] = game['release_date']+'-01-01'
    elif re.search(r'^[12]\d{3}-[0-3]\d$', game['release_date']):
        game['release_date'] = game['release_date']+'-01'
    try:
        cursor.execute('''INSERT INTO game (game_id, title, score, release_date) values (%s, %s, %s, %s)''', (game['id'], game['title'], game['moby_score'], game['release_date']))
    except psycopg2.IntegrityError:
        print(f'Game \'{game['title']}\' and game ID {game['id']} already exists in database.')

connection.commit()
connection.close()
