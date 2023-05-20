import datetime
import pandas as pd
import numpy as np
from imdb import Cinemagoer
import sys
import warnings
from tqdm import tqdm
import os
import surprise

from handle_movielens import *


def getMovieCorrelations(movieTitle, movies_df, userRatingsMatrix):
    movieId = getMovieId(movieTitle, movies_df)
    userRatingsMatrix.columns = userRatingsMatrix.columns.astype("int64")
    user_ratings = userRatingsMatrix[movieId]
    similar_to_movie = userRatingsMatrix.corrwith(user_ratings)
    correlatedMovies = pd.DataFrame(similar_to_movie, columns=['Correlation'])
    correlatedMovies.dropna(inplace=True)
    print(correlatedMovies.index)
    correlatedMovies.index = map(getMovieTitle, correlatedMovies.index, movies_df)
    correlatedMovies = correlatedMovies.join(ratings['nb of ratings'])
    correlatedMovies = correlatedMovies.sort_values('Correlation',
                                                    ascending=False)
    return correlatedMovies, similar_to_movie, user_ratings



def find_correlation_between_two_users(userRatingsMatrix: pd.DataFrame, user1: str, user2: str):
    """Find correlation between two users based on their rated movies using Pearson correlation"""
    rated_movies_by_both = userRatingsMatrix.loc[[user1, user2]].dropna(axis=1).T
    print(rated_movies_by_both.corr())
    user1_ratings = rated_movies_by_both.iloc[0]
    user2_ratings = rated_movies_by_both.iloc[1]
    print(np.corrcoef(user1_ratings.tolist(), user2_ratings.tolist()))
    # print(user1_ratings.corrwith(user2_ratings))
    # return np.corrcoef(user1_ratings, user2_ratings)[0, 1]
    # return pd.Series(user1_ratings).corr(pd.Series(user2_ratings))
    return rated_movies_by_both.corr().at[0, 1]


if(__name__ == "__main__"):
    movies, links, tags, userRatings, movieRatings = readCSVs(resourcePath="csv_files/ml-latest/", size=100000)
    print("csv read\n")
    print("making MovieMatrix...")
    userRatingsMatrix = getUserRatingsMatrix(userRatings)
    print("movieMatrix done!\n")
    movieTitle = 'Toy Story (1995)'
    movieId = getMovieId(movieTitle, movies)
    matrixCorr, matrixSimilar = getMovieCorrelations(movieTitle, movies, userRatingsMatrix)
    print(matrixCorr[matrixCorr["nb of ratings"] > 50].head(10))
    print("\n")
    # print(find_correlation_between_two_users(userRatingsMatrix, 1, 2))
    users = userRatings["userId"].unique()
    # similarity_matrix = np.empty((len(users), len(users)), dtype=float)
    # for user1 in tqdm(users, desc='user1', position=0):
    #     for user2 in tqdm(users, desc='user2', position=1):
    #         similarity_matrix += find_correlation_between_two_users(userRatingsMatrix, user1, user2)
    # # similarity_matrix = np.array([[find_correlation_between_two_users(userRatingsMatrix, user1, user2) for user1 in users] for user2 in users])
    # similarity_df = pd.DataFrame(similarity_matrix, columns=users, index=users)
    # print(similarity_df)
    # surprise.similarities.pearson(len(users), )
