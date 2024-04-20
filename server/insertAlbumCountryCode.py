import csv
import mysql.connector
import pandas as pd

# MySQL database connection details
HOST = '127.0.0.1'
USER = 'root'
PASSWORD = 'rusy'
DATABASE = 'spotify'

# Open database connection
df = pd.read_csv('spotify_albums_cleaned_up.csv')

# Connect to your MySQL database
conn = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)
cursor = conn.cursor()

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Extract ID and country_code
    id = row['id']
    country_code = row['available_markets']
    
    # Split country_code string into individual country_code
    country_code_list = eval(country_code)  # Convert string representation of list to actual list
    
    # Insert each genre into the MySQL table
    for country_code in country_code_list:
        # Define your insert query based on your table schema
        insert_query = f"INSERT IGNORE INTO availableIn (country_code, album_id) VALUES (%s, %s)"
        
        # Execute the insert query
        cursor.execute(insert_query, (country_code, id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Insertion successful for '{id}', country_code '{country_code}'")
        else:
            print(f"Insertion failed for '{id}', country_code '{country_code}'")

# Close the cursor and connection
cursor.close()
conn.close()