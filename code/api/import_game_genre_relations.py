import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()

connection = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
        )
cursor = connection.cursor()
cursor.execute('''SELECT MAX(game_id) FROM games_genres''')
last_game_id = cursor.fetchone()[0]
cursor.execute('''SELECT game_id, response from game_api_response WHERE game_id > %s ORDER BY game_id''', (last_game_id,))
#cursor.execute('''SELECT game_id, response from game_api_response ORDER BY game_id ''')
raw_responses = cursor.fetchall()

for response in raw_responses:
    for genre in response[1]['genres']:
        cursor.execute('''INSERT INTO games_genres (game_id, genre_id) VALUES (%s, %s)''', (response[0], genre['genre_id']))
    connection.commit()
connection.close()
