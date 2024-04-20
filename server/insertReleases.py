import csv
import mysql.connector
import pandas as pd

# MySQL database connection details
HOST = '127.0.0.1'
USER = 'root'
PASSWORD = 'rusy'
DATABASE = 'spotify'

# Open database connection
df = pd.read_csv('spotify_tracks_cleaned_up.csv')

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
    id = row['album_id']
    artist_id = row['artists_id']
    
    # Split genres string into individual genres
    artist_id_list = eval(artist_id)  # Convert string representation of list to actual list
    
    # Insert each genre into the MySQL table
    for artist in artist_id_list:
        # Define your insert query based on your table schema
        insert_query = f"INSERT IGNORE INTO releases (album_id, artist_id) VALUES (%s, %s)"
        
        # Execute the insert query
        cursor.execute(insert_query, (id,artist))
        conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()