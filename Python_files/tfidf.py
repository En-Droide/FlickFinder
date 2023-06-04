# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 18:43:28 2023

@author: MatyG
"""


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from difflib import get_close_matches
import ast

# def genre_popularity(csv_file):
#     popularity = (csv_file.genres.str.split('|').explode().value_counts()
#      .sort_values(ascending=False))
    
#     return popularity.head(10)


def process_data(csv_file):
    # .fillna('')
    df = csv_file
    if "title_wt_date" not in df.columns:
        df["title_wt_date"] = df["title"].str.replace(r"\s\(\d{4}\)$", "",
                                                      regex=True)
    # df.to_csv("out.csv", index=False)
    return df


def get_tfidf_matrix(df):
    # print(df.genres.str.split('|').dtypes)
    tfidf = TfidfVectorizer(stop_words='english')
    df['keywords_cast'] = df['keywords'] + ' ' + df['cast'] + ' ' + str(df.genres.str.split('|'))
    tfidf_matrix = tfidf.fit_transform(df['keywords_cast'])
    tfidf_matrix = csr_matrix(tfidf_matrix)
    return tfidf_matrix


def match_title(movie_title, df):
    movieList = df['title_wt_date'].values.tolist()
    closest_matches = get_close_matches(movie_title, movieList)
    if closest_matches:
        # Return the first closest match
        return closest_matches[0]
    else:
        return "No match found"

def titleDateSearch(movie_title, df):
    movie_id = df.loc[df['title_wt_date'] == movie_title, 'movieId'].iloc[0]
    movie_index = df.loc[df['movieId'] == movie_id].index[0]
    return df.loc[movie_index, 'title']

def get_similar_movies(movie_title, df, tfidf_matrix, number_movies=10):

    # Check if the movie is in the csv
    if movie_title not in df['title_wt_date'].values:
        raise ValueError('Movie title not found in DataFrame')

    # Get the movie ID and index
    movie_id = df.loc[df['title_wt_date'] == movie_title, 'movieId'].iloc[0]
    movie_index = df.loc[df['movieId'] == movie_id].index[0]

    # So, we have the tfidf_matrix (n_movies,n_movies), we start by just
    # choosing the row of the film (tfidf_matrix[movie_index], tfidf_matrix)
    # This will return a 2D matrix, weach the row represent the film we choose
    # and the column the other movies. But we just need the index and the score
    # of the other movies, so we flatten the matrix.
    similarity_scores = cosine_similarity(tfidf_matrix[movie_index],
                                          tfidf_matrix).flatten()

    # Creation of a list of similarity_scores containing (index, score)
    similarity_scores_list = []
    for i, score in enumerate(similarity_scores):
        similarity_scores_list.append((i, score))

    # The x[1] is because we sort according to the score not the index so the
    # second element of the list
    similarity_scores_list = sorted(similarity_scores_list, key=lambda x: x[1],
                                    reverse=True)

    # Get the indices of the top similar movies
    movie_indices = []
    for i in range(1, number_movies+1):
        movie_index = similarity_scores_list[i][0]
        movie_indices.append(movie_index)

    
    similar_movies = df.loc[movie_indices, 'title'].tolist()

    similar_movies.insert(0, titleDateSearch(movie_title, df))

    return similar_movies

def get_movie_genres_cast(df, movieTitle):
    movieId = df.index[df["title"] == movieTitle][0]
    cast_str = df.loc[movieId]["cast"]
    cast_list = ast.literal_eval(cast_str)[:3]
    return [x.lower() for x in df.loc[movieId]["genres"].split('|')], cast_list

def start_tfidf(df, tfidf_matrix, moviename, size):
    Film_title = match_title(moviename,df)
    print(Film_title)
    similar_movies = get_similar_movies(Film_title, df,
                                        tfidf_matrix, number_movies=size)
    
    return similar_movies


def setup_tfidf(file_name):
    print("setting up tfidf...")
    csv_file = pd.read_csv(file_name, encoding="utf-8")
    
    print(" csv done")
    # most_popular_movies = genre_popularity(csv_file)
    df = process_data(csv_file)
    print(" df done")
    tfidf_matrix = get_tfidf_matrix(df)
    print(" tfidf_matrix done")
    return tfidf_matrix, df

# print(start_tfidf("C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\python\\out_big_data.csv","Toy Story"))