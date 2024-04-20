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
unique_countryCode = set()

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Extract genres
    countryCode = row['available_markets']
    
    # Split genres string into individual genres
    countryCode_list = eval(countryCode)  # Convert string representation of list to actual list
    
    # Add genres to the set of unique genres
    unique_countryCode.update(countryCode_list)

# Insert unique genres into the 'genre' table
for countryCode in unique_countryCode:
    # Define insert query for the genre table
    insert_countryCode_query = "INSERT INTO Album_Available_Market (country_code) VALUES (%s)"
    
    # Execute the insert query
    cursor.execute(insert_countryCode_query, (countryCode,))
    conn.commit()

    # Check if the query executed successfully
    if cursor.rowcount > 0:
        print(f"Insertion successful for country_code '{countryCode}'")
    else:
        print(f"Insertion failed for country_code '{countryCode}'")

# Close the cursor and connection
cursor.close()
conn.close()