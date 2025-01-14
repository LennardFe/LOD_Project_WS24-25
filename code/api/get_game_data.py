import requests
import psycopg2
from dotenv import load_dotenv
import os
import json
from time import sleep

load_dotenv()

API_URL = 'https://api.mobygames.com/v1/games'
FETCH_LIMIT = 10
SLEEP_DURATION = 1.1

connection = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
        )
cursor = connection.cursor()
cursor.execute('''SELECT MAX(game_id) FROM game_api_response''')
last_game_id = cursor.fetchone()[0]
cursor.execute('''SELECT game_id from game WHERE game_id > %s ORDER BY game_id LIMIT %s''', (last_game_id,FETCH_LIMIT))
game_ids = cursor.fetchall()

for game_id in game_ids:
    params={'format':'normal','api_key':os.getenv("API_KEY"), 'id':game_id}
    response = requests.get(url=API_URL, params=params)
    game_data = response.json()
    cursor.execute('''INSERT INTO game_api_response (game_id, response) VALUES (%s, %s)''', (game_id, json.dumps(game_data['games'][0])))
    connection.commit()
    print(game_id[0])
    sleep(SLEEP_DURATION)
connection.close()
