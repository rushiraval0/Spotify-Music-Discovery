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
unique_genres = set()

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Extract genres
    genres = row['genres']
    
    # Split genres string into individual genres
    genres_list = eval(genres)  # Convert string representation of list to actual list
    
    # Add genres to the set of unique genres
    unique_genres.update(genres_list)

# Insert unique genres into the 'genre' table
for genre in unique_genres:
    # Define insert query for the genre table
    insert_genre_query = "INSERT INTO genres (genre) VALUES (%s)"
    
    # Execute the insert query
    cursor.execute(insert_genre_query, (genre,))
    conn.commit()

    # Check if the query executed successfully
    if cursor.rowcount > 0:
        print(f"Insertion successful for Genre '{genre}'")
    else:
        print(f"Insertion failed for Genre '{genre}'")

# Close the cursor and connection
cursor.close()
conn.close()