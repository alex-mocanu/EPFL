import pandas as pd


my_mail = 'alexandru.mocanu@epfl.ch'
plain_file = 'data/imdb-2.csv'
enc_file = 'data/com402-2.csv'

# Read files
plain_df = pd.read_csv(plain_file, skipinitialspace = True, quotechar = '"')
enc_df = pd.read_csv(enc_file, skipinitialspace = True, quotechar = '"')

# Group data by movie hash and sort them by count
enc_movies = list(enc_df.groupby('movie').count().sort_values(by='email', ascending=False).index)
plain_movies = list(plain_df.groupby('movie').count().sort_values(by='email', ascending=False).index)

# Match movie to its hash
movie_dict = {e:p for p, e in zip(plain_movies, enc_movies)}

# Change movie hash to movie name in encrypted dataframe
enc_df['movie'] = enc_df['movie'].apply(lambda x: movie_dict[x])

# Get my movies
my_movies_df = plain_df[plain_df['email'] == my_mail]

# Get entries in the encrypted dataframe with the same movies as I've rated
my_dfs = []
for movie in my_movies_df['movie']:
    my_dfs.append(enc_df[enc_df['movie'] == movie])

# Merge all the found dataframes by email
for i in range(1, len(my_dfs)):
    my_dfs[0] = my_dfs[0].merge(my_dfs[i], left_on='email', right_on='email')

# Get my encrypted email
my_enc_email = my_dfs[0]['email'][0]

# Get my movies from the encrypted dataframe
my_movies = enc_df[enc_df['email'] == my_enc_email]['movie']

with open('ex1b.txt', 'w') as f:
    for movie in my_movies:
        f.write(movie + '\n')
