import pandas as pd


my_mail_enc = 'a1b9e108980688445ed2865734a460f3ac9fb29f7f1bdab29c3b273ae410dfcd'
plain_file = 'data/imdb-1.csv'
enc_file = 'data/com402-1.csv'

# Read files
plain_df = pd.read_csv(plain_file, skipinitialspace = True, quotechar = '"')
enc_df = pd.read_csv(enc_file, skipinitialspace = True, quotechar = '"')

# Select only my movies from the IMDB dataframe
my_movie_enc_df = enc_df[enc_df['email'] == my_mail_enc]

# Extract ratings for the movies that I rated in the Netflix dataset
with open('ex1a.txt', 'w') as f:
    for movie in my_movie_enc_df['movie']:
        movie_df = enc_df[enc_df['movie'] == movie]
        # Get the majority vote to find the movie
        movie = movie_df.merge(plain_df, left_on='date', right_on='date')['movie_y'].mode()
        f.write(movie[0] + '\n')
