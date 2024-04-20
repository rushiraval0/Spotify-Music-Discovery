use spotify;

CREATE TABLE Artist(
	artist_id char(23),
	artist_name varchar(255),
	followers int,
	artist_popularity int,
	PRIMARY KEY(artist_id));

LOAD DATA LOCAL INFILE 'C:\\Users\\rusy\\Desktop\\ECE656 - Spotify\\Dataset\\Data Sources\\spotify_artists_test.csv'
INTO TABLE Artist
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(artist_id, artist_name, followers, artist_popularity);

create table Album(
    album_id char(23) primary key, 
    album_name varchar(255),
    album_type enum('single','album','compilation'),
    release_info varchar(10),
    total_tracks int,
    album_uri char(37) GENERATED ALWAYS AS (concat('spotify:album:',album_id)) STORED,
    album_access_url varchar(68) GENERATED ALWAYS AS (concat('{\'spotify\': \'https://open.spotify.com/album/',album_id,'\'}')) STORED,
    album_access_api varchar(56) GENERATED ALWAYS AS (concat('https://api.spotify.com/v1/albums/',album_id)) STORED
    );    
    
LOAD DATA LOCAL INFILE 'C:\\Users\\rusy\\Desktop\\ECE656 - Spotify\\Dataset\\Data Sources\\spotify_albums_cleaned_up.csv'
INTO TABLE Album
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(album_id, album_name, album_type, release_info, total_tracks);

create table Album_Available_Market(
   country_code char(2) primary key 
);
-- Python

create table availableIn(
    country_code char(2),
    album_id char(23),
    primary key(album_id,country_code),
    foreign key (album_id) references Album(album_id),
    foreign key (country_code) references Album_Available_Market(country_code)    
);
-- Python

CREATE TABLE Genres(genre varchar(255),
	PRIMARY KEY (genre));    
-- Python

CREATE TABLE Artist_Genres(artist_id char(23),
		genre varchar(255),
        PRIMARY KEY(artist_id,genre),
		FOREIGN KEY (genre) REFERENCES Genres(genre),
	FOREIGN KEY (artist_id) REFERENCES Artist(artist_id));
-- Python

create table Track(
    track_id char(23) primary key,
    track_name varchar(255),
    track_preview_url varchar(255),
    duration_ms int,
    track_uri char(36) GENERATED ALWAYS AS (concat('spotify:track:',track_id)) STORED,
    track_access_url varchar(69) GENERATED ALWAYS AS (concat('{\'spotify\': \'https://open.spotify.com/tracks/',track_id,'\'}')) STORED,
    track_access_api varchar(56) GENERATED ALWAYS AS (concat('https://api.spotify.com/v1/tracks/',track_id)) STORED
    );    
    
LOAD DATA LOCAL INFILE 'C:\\Users\\rusy\\Desktop\\ECE656 - Spotify\\Dataset\\Data Sources\\spotify_tracks_cleaned_up.csv'
INTO TABLE Track
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(track_id, track_name, track_preview_url, duration_ms);


CREATE TABLE Track_Analysis_Elements (
	track_id char(23),
	track_analysis_link char(64) GENERATED ALWAYS AS (concat('https://api.spotify.com/v1/audio-analysis/',track_id)) STORED,
	valence decimal(5,4),
	time_signature int,
	speechiness decimal(5,4),
	track_popularity int,
	mode enum('0','1'),
	loudness decimal(5,3),
	liveness decimal(5,4),
	`key` int,
	instrumentalness decimal(9,8),
	disc_number int,
	danceability decimal(5,4),
	acousticness decimal(9,8),
    energy decimal(5,4),
	PRIMARY KEY(track_id, track_analysis_link),
	FOREIGN KEY(track_id) REFERENCES Track(track_id),
    CONSTRAINT check_time_signature CHECK(time_signature >=3 AND time_signature <=7),
	CONSTRAINT check_valence CHECK(valence >=0 AND valence <=1),
	CONSTRAINT check_speechiness CHECK(speechiness >=0 AND speechiness <=1),
	CONSTRAINT check_liveness CHECK(liveness >=0 AND liveness <=1),
	CONSTRAINT check_key CHECK(`key` >=1 AND `key` <=11),
	CONSTRAINT check_danceability CHECK(`key` >=0 AND `key` <=1),
	CONSTRAINT check_acousticness CHECK(`key` >=0 AND `key` <=1),
    CONSTRAINT check_energy CHECK(`key` >=0 AND `key` <=1));
    
LOAD DATA LOCAL INFILE 'C:\\Users\\rusy\\Desktop\\ECE656 - Spotify\\Dataset\\Data Sources\\spotify_tracks_analysis.csv'
INTO TABLE Track_Analysis_Elements
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(track_id, track_analysis_link, valence, time_signature, speechiness, track_popularity, mode, loudness, liveness, `key`, instrumentalness, disc_number, danceability, acousticness, energy);

    
create table consists(
    track_id char(23),
    album_id char(23),
    primary key(album_id,track_id),
    foreign key (album_id) references Album(album_id),
    foreign key (track_id) references track(track_id)
);

LOAD DATA LOCAL INFILE 'C:\\Users\\rusy\\Desktop\\ECE656 - Spotify\\Dataset\\Data Sources\\spotify_consist.csv'
INTO TABLE consists
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(track_id, album_id);

CREATE TABLE composes (
	artist_id char(23),
	track_id char(23),
	PRIMARY KEY(artist_id,track_id),
	FOREIGN KEY(artist_id) REFERENCES Artist(artist_id),
	FOREIGN KEY(track_id) REFERENCES Track(track_id));

LOAD DATA LOCAL INFILE 'C:\\Users\\rusy\\Desktop\\ECE656 - Spotify\\Dataset\\Data Sources\\track_artist.csv'
INTO TABLE composes
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(artist_id, track_id);
-- Python

CREATE TABLE releases (
	artist_id char(23),
	album_id char(23),
	PRIMARY KEY(artist_id,album_id),
	FOREIGN KEY(artist_id) REFERENCES Artist(artist_id),
	FOREIGN KEY(album_id) REFERENCES Album(album_id));
-- python
    
CREATE view view_app
AS
  (SELECT t1.track_id,
          t4.artist_name,
          track_name,
          genre
   FROM   track t1
          INNER JOIN composes t2
                  ON t1.track_id = t2.track_id
          INNER JOIN artist_genres t3
                  ON t2.artist_id = t3.artist_id
          INNER JOIN artist t4
                  ON t4.artist_id = t2.artist_id);

CREATE view view_db
AS
  (SELECT track_id,
          artist_name,
          track_name,
          track_popularity,
          danceability,
          energy,
          `key`,
          loudness,
          mode,
          speechiness,
          acousticness,
          instrumentalness,
          liveness,
          valence,
          time_signature,
          genre
   FROM   view_app
          INNER JOIN track_analysis_elements USING(track_id)); 
    
