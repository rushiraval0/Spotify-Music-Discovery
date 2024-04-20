import streamlit as st
import pandas as pd
import numpy as np
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.metrics.pairwise import cosine_similarity
import random
import time
from sklearn.preprocessing import normalize
import mysql.connector

HOST = '127.0.0.1'
USER = 'root'
PASSWORD = 'rusy'
DATABASE = 'spotify'

# Open database connection

# Connect to your MySQL database
conn = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)
cursor = conn.cursor()

allDF = pd.read_sql("select * from view_db", conn)
allDF = allDF.rename(columns={
    'artist_name': 'artists',
    'track_popularity': 'popularity',
    'genre': 'track_genre'
})

st.set_page_config(
    page_title="SPTFY",
    page_icon="🎵",
)

mock_data = {
    'Track Name': ['Song 1', 'Song 2', 'Song 3', 'Song 4', 'Song 5', 'Song 6', 'Song 7', 'Song 8', 'Song 9', 'Song 10',
                   'Song 11', 'Song 12', 'Song 13', 'Song 14', 'Song 15', 'Song 16', 'Song 17', 'Song 18', 'Song 19', 'Song 20'],
    'Track Artist': ['Artist 1', 'Artist 2', 'Artist 3', 'Artist 4', 'Artist 5', 'Artist 6', 'Artist 7', 'Artist 8', 'Artist 9', 'Artist 10',
                     'Artist 11', 'Artist 12', 'Artist 13', 'Artist 14', 'Artist 15', 'Artist 16', 'Artist 17', 'Artist 18', 'Artist 19', 'Artist 20']
}




def filter_csv(input_df, column_name, values_set):
    # Read the CSV file into a DataFrame   
    # Filter DataFrame based on values in the specified column
    filtered_df = input_df[input_df[column_name].isin(values_set)]    
    # Write the filtered DataFrame to a new CSV file
    return filtered_df

def shuffle_track_ids(track_ids):
    # Shuffle the list of track IDs in place
    random.shuffle(track_ids)

def remove_track_ids(similarities, track_ids_to_remove):
    for track_id in track_ids_to_remove:
        similarities.pop(track_id, None)

def calculate_cosine_similarity(all_filtered_df, means_genre_df):
    # Selecting features for cosine similarity calculation
    features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 
                'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']

    # Iterate over each track_id in all_filtered_df
    cosine_similarities = {}
    for _, track_row in all_filtered_df.iterrows():
        track_id = track_row['track_id']
        genre = track_row['track_genre']
        if genre in means_genre_df['track_genre'].values:
            
            # Selecting mean features for the track's genre
            mean_features = means_genre_df[means_genre_df['track_genre'] == genre][features].iloc[0]
            
            # Selecting features for the track
            track_features = track_row[features]
            
            # Calculating cosine similarity between track and mean features
            track_features_normalized = normalize(track_features.values.reshape(1, -1), norm='l2')
            mean_features_normalized = normalize(mean_features.values.reshape(1, -1), norm='l2')
            similarity = cosine_similarity([track_features.values], [mean_features.values])[0][0]

            # Storing the cosine similarity for the track_id
            cosine_similarities[track_id] = similarity

    # Discard None values
    cosine_similarities = {k: v for k, v in cosine_similarities.items() if v is not None}

    # Sort similarities in descending order
    cosine_similarities = dict(sorted(cosine_similarities.items(), key=lambda item: item[1], reverse=True))

    return cosine_similarities



with st.form("myform", clear_on_submit=False):
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
            # my_bar = st.progress(0, text=progress_text)

    if uploaded_file is not None:
        progress_text = "Progress"
        my_bar = st.progress(0, text=progress_text)
        
        with st.spinner("Uploading..."):
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)

        st.success("File uploaded successfully!")

        
    submit = st.form_submit_button(label='Submit', use_container_width=True)
    st.session_state['submit_button'] = submit

        # Reshuffle button

    if submit:
        if uploaded_file is not None:

            userDF = pd.read_csv(uploaded_file)
            artistMsPlayedDict = userDF.groupby('artistName')['msPlayed'].sum().to_dict()
            userArtistsDict = dict(sorted(artistMsPlayedDict.items(), key=lambda x: x[1], reverse=True)[:20])

            userArtists = list(userArtistsDict.keys())

            userGenreDF = filter_csv(allDF,"artists",userArtists)

            userGenreSet = set(userGenreDF['track_genre'].unique())


            allArtistDF = filter_csv(allDF,"track_genre",list(userGenreSet))

            allArtistSet = list(allArtistDF['artists'].unique())

            # individual_artists = [artist.split(';') for artist in allArtistSet]

            # Flatten the list of lists into a single list
            # flattened_artist_list = {artist for sublist in individual_artists for artist in sublist}

            # print(userArtists)


            grouped = allDF.groupby('artists')

            # Initialize an empty list to store the top 10 track IDs for each artist
            top_10_track_ids = {}

            # Iterate over each artist in the list
            for artist in userArtists:
                # Filter the dataset for the current artist
                artist_data = allDF[allDF['artists'] == artist]
                # Sort the filtered data by popularity in descending order
                sorted_data = artist_data.sort_values(by='popularity', ascending=False)
                # Select the top 10 track IDs for the artist
                top_10_tracks = sorted_data.head(10)['track_id'].tolist()
                # Add the top 10 track IDs to the dictionary
                top_10_track_ids[artist] = top_10_tracks

            # Combine all the track IDs into a single list
            all_track_ids = [track_id for track_ids in top_10_track_ids.values() for track_id in track_ids]

            # print(all_track_ids)

            track_uris = set()

            # Read and parse the JSON file
            # try:
            #     with open('Playlist1.json', 'r') as file:
            #         data = json.load(file)

            #     # Ensure 'playlists' key exists and it's a list
            #     if 'playlists' in data and isinstance(data['playlists'], list):
            #         # Iterate over each playlist
            #         for playlist in data['playlists']:
            #             # Ensure 'items' key exists and it's a list
            #             if 'items' in playlist and isinstance(playlist['items'], list):
            #                 # Iterate over each item in the playlist
            #                 for item in playlist['items']:
            #                     # Ensure 'track' key exists and it's a dictionary
            #                     if 'track' in item and isinstance(item['track'], dict):
            #                         # Extract trackUri value and add it to the set
            #                         track_uris.add(item['track'].get('trackUri', ''))
            # except FileNotFoundError:
            #     print("File not found.")
            # except json.JSONDecodeError:
            #     print("Error decoding JSON.")


            genre_set = set(allDF['track_id'])
            track_ids = {uri.split(':')[-1] for uri in track_uris}


            hit_set = genre_set.intersection(all_track_ids)
            spotify_data = pd.read_csv('spotify_dataset.csv')


            filtered_data = spotify_data[spotify_data['track_id'].isin(list(hit_set))]



            # print(filtered_data.columns)

            # Finding the mean of each column
            user_filter_columns = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']

            # Grouping by 'track_genre' and finding the mean of each column
            means_genre_df = filtered_data.groupby('track_genre')[user_filter_columns].mean()
            means_genre_df.reset_index(inplace=True)

            all_filter_columns = ['track_genre','artists','track_id','danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']

            all_filtered_df = spotify_data[all_filter_columns]
            # Printing the DataFrame

            # print(len(all_filtered_df))
            filtered_df = all_filtered_df[all_filtered_df['track_genre'].isin(userGenreSet)]
            filtered_df = all_filtered_df[all_filtered_df['artists'].isin(userArtists)]
            # print(len(filtered_df))
            # print(means_genre_df)
            # print(all_filtered_df)

            # print(userArtists)



            similarities = calculate_cosine_similarity(filtered_df, means_genre_df)

            # similarities = similarities

            count = 0

            remove_track_ids(similarities, hit_set)

            # for track_id, similarity in similarities.items():
            #         print(f"Track ID: {track_id} -> Similarity: {similarity}")

            # print(len(similarities))

            tracks = list(similarities)

            tracks = set(tracks)
            tracks = list(tracks)

            shuffle_track_ids(tracks)


            track_info_dict = {}

            filterc=['track_id','track_name','artists']

            filtered_df = spotify_data[filterc]

            last_filter = filtered_df[filtered_df['track_id'].isin(tracks)]

            def sample_up_to_3(group):
                return group.sample(min(3, len(group)))

            user1_songs = last_filter[last_filter['artists'].isin(userArtists)].groupby('artists').apply(sample_up_to_3)[:20]
            print(user1_songs)

            last_filter = user1_songs

            last_filter['track_id'] = "https://open.spotify.com/track/" + last_filter['track_id']

            selected_columns = last_filter[['track_name', 'artists','track_id']]

    # Remove duplicate track names
            last_filter = last_filter.drop_duplicates(subset=['track_name'])

            # Convert to dictionary
            output_dict = last_filter.set_index('track_name')['artists'].to_frame()

            # last_filter.reset_index(drop=True)

            # print(output_dict)

            last_filter['track_link'] = last_filter['track_id'].apply(lambda x: f'<a href="{x}">{x}</a>')

# Drop the old 'track_id' column
            last_filter.drop(columns=['track_id'], inplace=True)

            # Drop the index
            last_filter = last_filter.reset_index(drop=True)

            # Convert DataFrame to HTML table without index
            html_table = last_filter.to_html(index=False, escape=False)

            # Display HTML table in Streamlit
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.write("Please submit a CSV File!")
        cursor.close()
        conn.close()
