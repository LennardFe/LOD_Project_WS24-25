import os
import psycopg2
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Connect to neon database 
neon_connection = psycopg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST")
)
neon_cursor = neon_connection.cursor()


# Connect to neo4j database
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)


# Function to create nodes in Neo4j 
def create_node(tx, label, properties):
    query = f"MERGE (n:{label} {{" # Using MERGE to avoid creating duplicate relationships
    query += ", ".join([f"{key}: ${key}" for key in properties.keys()])
    query += "})"
    tx.run(query, **properties)


# Function to create relationships in Neo4j
def create_relationship(tx, node1_label, node1_property, node2_label, node2_property, relationship_type):
    query = (f"MATCH (a:{node1_label} {{ {node1_property[0]}: ${node1_property[0]} }}), "
             f"(b:{node2_label} {{ {node2_property[0]}: ${node2_property[0]} }}) "
             f"MERGE (a)-[:{relationship_type}]->(b)")  # Using MERGE to avoid creating duplicate relationships
    params = {node1_property[0]: node1_property[1], node2_property[0]: node2_property[1]}
    tx.run(query, **params)



# Function to fetch data from neon database
def fetch_data_from_neon(table_name, columns):

    # Connect to neon database inside the function to create a new session each time
    # This prevents the connection from being closed after five minutes of inactivity
    neon_connection = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )
    neon_cursor = neon_connection.cursor()
    
    column_list = ", ".join(columns)
    query = f"SELECT {column_list} FROM {table_name}"
    neon_cursor.execute(query)
    data = neon_cursor.fetchall()

    neon_cursor.close()
    neon_connection.close()

    return data


# Function to transfer data from neon to neo4j
def transfer_data_dynamically():
    with neo4j_driver.session() as session:
        
        # Transfer data for companies
        companies = fetch_data_from_neon("company", ["company_id", "company_name"])
        for company in companies:
            session.execute_write(
                create_node, "Company", {"company_id": company[0], "name": company[1]}
            )

        # Transfer data for games
        games = fetch_data_from_neon("game", ["game_id", "title", "score", "release_date"])
        for game in games:
            session.execute_write(
                create_node, "Game", {"game_id": game[0], "name": game[1], "score": game[2], "release_date": game[3]}
            )

        # Transfer data for genres
        genres = fetch_data_from_neon("genre", ["genre_id", "genre_type_id", "name"]) #  TODO: Description is left out, maybe add it?
        for genre in genres:
            session.execute_write(
                create_node, "Genre", {"genre_id": genre[0], "genre_type_id": genre[1], "name": genre[2]}
            )

        # Transfer data for genres types
        genre_types = fetch_data_from_neon("genre_type", ["genre_type_id", "name"])
        for genre_type in genre_types:
            session.execute_write(
                create_node, "GenreType", {"genre_type_id": genre_type[0], "name": genre_type[1]}
            )

        # Transfer data for platforms
        platforms = fetch_data_from_neon("platform", ["platform_id", "name"])
        for platform in platforms:
            session.execute_write(
                create_node, "Platform", {"platform_id": platform[0], "name": platform[1]}
            )

        # TODO: Maybe rename the relationship to "DEVELOPED_BY" or "PUBLISHED_BY", to fit the other relationships?
        # Link games to companies using the bridge table
        games_companies = fetch_data_from_neon("games_companies", ["game_id", "company_id", "type"])
        for game_company in games_companies:
            session.execute_write(
                create_relationship, "Game", ("game_id", game_company[0]), "Company", ("company_id", game_company[1]), game_company[2] 
            )

        # Link games to genres using the bridge table
        games_genres = fetch_data_from_neon("games_genres", ["game_id", "genre_id"])
        for game_genre in games_genres:
            session.execute_write(
                create_relationship, "Game", ("game_id", game_genre[0]), "Genre", ("genre_id", game_genre[1]), "HAS_GENRE"
            )

        # Link games to platforms using the bridge table
        games_platforms = fetch_data_from_neon("games_platforms", ["game_id", "platform_id"])
        for game_platform in games_platforms:
            session.execute_write(
                create_relationship, "Game", ("game_id", game_platform[0]), "Platform", ("platform_id", game_platform[1]), "AVAILABLE_ON"
            )

        # Link genres to genre types
        genres = fetch_data_from_neon("genre", ["genre_id", "genre_type_id"])
        for genre in genres:
            session.execute_write(
                create_relationship, "Genre", ("genre_id", genre[0]), "GenreType", ("genre_type_id", genre[1]), "IS_TYPE"
            )


# run the script
if __name__ == "__main__":
    try:
        transfer_data_dynamically()
        print("Data transfer successful")
    finally:
        neo4j_driver.close()