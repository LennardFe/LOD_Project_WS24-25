import os
import psycopg2
from neo4j import GraphDatabase
from dotenv import load_dotenv
from schema_definitions import TABLES, RELATIONSHIP_TABLES, SCHEMA_MAPPING

# Load environment variables
load_dotenv()

# Connect to neo4j database
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def create_batch_nodes(tx, label, data_list):
    """
    Creates a batch of nodes in Neo4j.

    Parameters:
        tx (neo4j.Session): The Neo4j transaction.
        label (str): The label of the nodes.
        data_list (list): The data to create the nodes.

    Returns:
        None
    """
    # Delete all nodes on the database
    tx.run(f"MATCH (n:{label}) DETACH DELETE n")

    # Create the new nodes
    query = f"UNWIND $properties AS row CREATE (n:{label}) SET n = row"
    tx.run(query, properties=data_list)

def create_relationship(tx, node1_label, node1_property, node2_label, node2_property, relationship_type):
    """
    Creates a relationship between two nodes in Neo4j.
    
    Parameters:
        tx (neo4j.Session): The Neo4j transaction.
        node1_label (str): The label of the first node.
        node1_property (tuple): The property of the first node.
        node2_label (str): The label of the second node.
        node2_property (tuple): The property of the second node.
        relationship_type (str): The type of the relationship.

    Returns:
        None
    """
    query = (f"MATCH (a:{node1_label} {{ {node1_property[0]}: ${node1_property[0]} }}), "
             f"(b:{node2_label} {{ {node2_property[0]}: ${node2_property[0]} }}) "
             f"MERGE (a)-[:{relationship_type}]->(b)")  # Using MERGE to avoid creating duplicate relationships
    params = {node1_property[0]: node1_property[1], node2_property[0]: node2_property[1]}
    tx.run(query, **params)

def fetch_data_from_neon(table_name, columns):
    """
    Fetches data from the neon database. Connects to the database inside the 
    function to create a new session each time. This prevents the connection 
    from being closed after five minutes of inactivity.
    
    Parameters:
        table_name (str): The name of the table to fetch data from.
        columns (list): The columns to fetch data from.

    Returns:
        list: The fetched data.
    """
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

def map_nodes_to_schema_org(node_label, row_data):
    """
    Maps the schema.org properties to the node labels.

    Parameters:
        node_label (str): The label of the node.
        row_data (list): The data of the row.

    Returns:
        dict: The mapped schema.org properties.
    """
    if node_label in SCHEMA_MAPPING:
        mapping = SCHEMA_MAPPING[node_label]

        mapped_data = {}
        for key, schema_key in mapping.items():
            if schema_key in row_data:
                mapped_data[key] = row_data[schema_key]  # map schema field to value

        return mapped_data

    else:
        return row_data

def transfer_data():
    """
    Transfers data from the neon database to the neo4j database.

    Parameters:
        None

    Returns:
        None
    """
    with neo4j_driver.session() as session:
        data_list = [] # List to store the data to create nodes
        
        # Create nodes based on the tables
        for row in TABLES:
            table_name, columns, label = row

            data = fetch_data_from_neon(table_name, columns)
            for row in data:
                data = dict(zip(columns, row))
                schema_data = map_nodes_to_schema_org(label, data)
                data_list.append(schema_data)

            session.execute_write(create_batch_nodes, label, data_list)
            data_list = []

        # TODO: This part is somewhow insanenly slow, i dont know why
        for row in RELATIONSHIP_TABLES:
            table_name, columns, table1, table2, column, type = row

            data = fetch_data_from_neon(table_name, columns)
            for row in data:
                data = dict(zip(columns, row))
                relationship_type = type if type else data[columns[2]]

                session.execute_write(
                    create_relationship,
                    table1, (column, data[columns[0]]),
                    table2, (column, data[columns[1]]),
                    relationship_type
                )
 
        # TODO: Refactor this to be more dynamic, currently hardcoded since its the only relation that is one-to-many
        genres = fetch_data_from_neon("genre", ["genre_id", "genre_type_id"])
        for genre in genres:
            session.execute_write(
                create_relationship, "Genre", ("identifier", genre[0]), "identifier", ("genre_type_id", genre[1]), "IS_TYPE"
            )

if __name__ == "__main__":
    try:
        transfer_data()
        print("Data transfer successful")
    finally:
        neo4j_driver.close()