import csv
import mysql.connector
import pandas as pd

# MySQL database connection details
HOST = '127.0.0.1'
USER = 'root'
PASSWORD = 'rusy'
DATABASE = 'spotify'

# Open database connection
df = pd.read_csv('spotify_artists_cleaned_up.csv')

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
    # Extract ID and genres
    id = row['id']
    genres = row['genres']
    
    # Split genres string into individual genres
    genres_list = eval(genres)  # Convert string representation of list to actual list
    
    # Insert each genre into the MySQL table
    for genre in genres_list:
        # Define your insert query based on your table schema
        insert_query = f"INSERT IGNORE INTO Artist_Genres (artist_id, genre) VALUES (%s, %s)"
        
        # Execute the insert query
        cursor.execute(insert_query, (id, genre))
        conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()