import sys
import json
import datetime
import pandas as pd


my_email = 'alexandru.mocanu@epfl.ch'
plain_file = 'data/imdb-3.csv'
enc_file = 'data/com402-3.csv'

# Read files
plain_df = pd.read_csv(plain_file, skipinitialspace = True, quotechar = '"')
enc_df = pd.read_csv(enc_file, skipinitialspace = True, quotechar = '"')

plain_df['date'] = pd.to_datetime(plain_df['date'], format="%d/%m/%y")
enc_df['date'] = pd.to_datetime(enc_df['date'], format="%d/%m/%y")

# Find all users
users = plain_df['email'].unique()

if sys.argv[1] == '1':
    # Match users and hashes
    user_dict = {}
    for user in users:
        # Select my movies
        my_movies_df = plain_df[plain_df['email'] == user]
        movie_list = my_movies_df['movie']

        # Generate entries for my_movies_df with offsetted dates
        new_data = []
        for i in range(-13, 14):
            for movie in my_movies_df.values:
                day = movie[2] + datetime.timedelta(days=i)
                new_entry = movie.copy()
                new_entry[2] = day
                new_data.append(new_entry)

        my_movies_df = pd.DataFrame(new_data, columns=['email', 'movie', 'date', 'rating'])

        # Merge with encrypted dataframe on date
        my_movies_df = my_movies_df.merge(enc_df, left_on='date', right_on='date')

        # Separate dataframe by movie
        dfs = []
        for movie in movie_list:
            dfs.append(my_movies_df[my_movies_df['movie_x'] == movie])

        # Merge dataframes by encryted email
        int_df = dfs[0][['email_y']]
        for i in range(1, len(dfs)):
            int_df = int_df.merge(dfs[i][['email_y']], left_on='email_y', right_on='email_y')
            # Stop if there is only one email left
            if len(int_df['email_y'].unique()) == 1:
                break

        enc_mail = int_df['email_y'][0]
        user_dict[user] = enc_mail

    json.dump(user_dict, open('email.json', 'w'))
else:
    # Decode movie hashes
    # Load emails
    with open('email.json', 'r') as f:
        user_dict = json.loads(f.read())
    # Reverse dictionary
    inverse_user_dict = {user_dict[p]:p for p in user_dict}
    # Replace email hashes with emails
    enc_df['email'] = enc_df['email'].apply(lambda x: inverse_user_dict[x])
    # Get the list of movie hashes
    movie_hashes = enc_df['movie'].unique()
    movie_dict = {}
    for movie_hash in movie_hashes:
        # Get best fitting movie
        df = enc_df[enc_df['movie'] == movie_hash].merge(plain_df, left_on=['email', 'rating'], right_on=['email', 'rating'])
        best_fit = df[abs(df['date_x'] - df['date_y']) <= datetime.timedelta(days=14)]['movie_y'].mode()[0]
        movie_dict[movie_hash] = best_fit

    # Get my movies
    my_movies = enc_df[enc_df['email'] == my_email]['movie']
    with open('ex1c.txt', 'w') as f:
        for movie in my_movies:
            f.write(movie_dict[movie] + '\n')
