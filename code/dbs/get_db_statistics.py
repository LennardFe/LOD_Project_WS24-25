import os
import psycopg2
import csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to PostgreSQL database
try:
    conn = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )
    cursor = conn.cursor()
    print("Connected to the database.")
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit()

# Query to get all table names
try:
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """
    )

    tables = cursor.fetchall()
    if not tables:
        print("No tables found in the database.")
        exit()
except Exception as e:
    print(f"Error fetching table names: {e}")
    conn.close()
    exit()

# Fetch row counts
all_counts = []
for (table_name,) in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        all_counts.append((table_name, row_count))
    except Exception as e:
        print(f"Error counting rows in table {table_name}: {e}")
        all_counts.append((table_name, "ERROR"))

# Sort by Row Count descending but move "game_api_response" to the end
all_counts_sorted = sorted(
    all_counts,
    key=lambda x: (x[0] != "game_api_response", x[1] if isinstance(x[1], int) else -float("inf")),
    reverse=False,
)

# Save to CSV
output_file = "table_row_counts.csv"
with open("../../qmd/"+output_file, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Table Name", "Row Count"])  # Header row
    writer.writerows(all_counts_sorted)

print(f"Row counts have been written to {output_file}")

# Close the database connection
cursor.close()
conn.close()
