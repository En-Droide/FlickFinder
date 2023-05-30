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


def getMovieCorrelations(movieTitle, movies_df, movieRatings_df, userRatingsMatrix):
    movieId = getMovieId(movieTitle, movies_df)
    # userRatingsMatrix.columns = userRatingsMatrix.columns.astype("int64")
    user_ratings = userRatingsMatrix[movieId]
    similar_to_movie = userRatingsMatrix.corrwith(user_ratings)
    correlatedMovies = pd.DataFrame(similar_to_movie, columns=['Correlation'])
    correlatedMovies.dropna(inplace=True)
    correlatedMovies = correlatedMovies.join(movieRatings_df['nb of ratings'])
    correlatedMovies = correlatedMovies.sort_values('Correlation',
                                                    ascending=False)
    correlatedMovies = correlatedMovies.reset_index(level=["movieId"])
    correlatedMovies["movieTitle"] = correlatedMovies.apply(lambda x: getMovieTitle(x["movieId"], movies_df), axis=1)
    correlatedMovies = correlatedMovies[["movieId", "movieTitle", "Correlation", "nb of ratings"]]
    return correlatedMovies, similar_to_movie


def getUserCorrelations(userId, movies_df, movieRatings_df, userRatingsMatrix):
    userRatingsMatrix = userRatingsMatrix.T
    user_ratings = userRatingsMatrix[userId]
    similar_to_user = userRatingsMatrix.corrwith(user_ratings)
    correlatedUsers = pd.DataFrame(similar_to_user, columns=['Correlation'])
    correlatedUsers.dropna(inplace=True)
    correlatedUsers = correlatedUsers.sort_values('Correlation',
                                                    ascending=False)
    # correlatedUsers = correlatedUsers.reset_index(level=["userId"])
    # correlatedUsers = correlatedUsers[["userId", "Correlation"]]
    return correlatedUsers, similar_to_user


def find_correlation_between_two_users(userRatingsMatrix, user1, user2):
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
    
    # movieTitle = 'Toy Story (1995)'
    # movieId = getMovieId(movieTitle, movies)
    # matrixCorr, matrixSimilar = getMovieCorrelations(movieTitle, movies, movieRatings, userRatingsMatrix)
    # print("\n\nMovies similar to : " + movieTitle)
    # print(matrixCorr[matrixCorr["nb of ratings"] > 50].head(10))
    # print("\n")
    
    # userId = 1
    # matrixCorr2, matrixSimilar2 = getUserCorrelations(userId, movies, movieRatings, userRatingsMatrix)
    # print("\n\nUsers similar to : " + str(userId))
    
    # print(matrixCorr2.head(10))
    # print("\n")
    
    userId = 1
    matrixCorr2, matrixSimilar2 = getUserCorrelations(userId, movies, movieRatings, userRatingsMatrix)
    print("\n\nUsers similar to : " + str(userId))
    
    print(matrixCorr2.head(10))
    print("\n")
    # print(find_correlation_between_two_users(userRatingsMatrix, 1, 2))
    # users = userRatings["userId"].unique()
    # similarity_matrix = np.empty((len(users), len(users)), dtype=float)
    # for user1 in tqdm(users, desc='user1', position=0):
    #     for user2 in tqdm(users, desc='user2', position=1):
    #         similarity_matrix += find_correlation_between_two_users(userRatingsMatrix, user1, user2)
    # # similarity_matrix = np.array([[find_correlation_between_two_users(userRatingsMatrix, user1, user2) for user1 in users] for user2 in users])
    # similarity_df = pd.DataFrame(similarity_matrix, columns=users, index=users)
    # print(similarity_df)
    # surprise.similarities.pearson(len(users), )
