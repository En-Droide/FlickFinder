# -*- coding: utf-8 -*-
"""
Created on Sat May 20 12:31:30 2023

@author: lotod
"""

from handle_movielens import *
from collab_surprise import *
from collab_similarities import *


def getSimilarPredictions(userId, movieTitle, movies_df, userRatings_df, movieRatings_df, userRatingsMatrix, size, minRatings):
    movieId = getMovieId(movieTitle, movies)
    matrixCorr, matrixSimilar = getMovieCorrelations(movieTitle, movies, movieRatings, userRatingsMatrix)
    topSimilar = matrixCorr[matrixCorr["nb of ratings"] >= minRatings].head(size)
    model = createModel(userRatings_df, SVD)
    topSimilar["prediction"] = topSimilar.apply(lambda row: model.predict(999999, row["movieId"])[3], axis=1)
    topSimilar.sort_values("prediction", ascending=False, inplace=True)
    return topSimilar





if(__name__ == "__main__"):
    movies, links, tags, userRatings, movieRatings = readCSVs(resourcePath="csv_files/ml-latest/", size=1000000)
    print("csv read\n")
    print("making MovieMatrix...")
    userRatingsMatrix = getUserRatingsMatrix(userRatings)
    print("movieMatrix done!\n")
    movieTitle = 'Shrek 2 (2004)'
    # movieId = getMovieId(movieTitle, movies)
    # matrixCorr, matrixSimilar = getMovieCorrelations(movieTitle, movies, movieRatings, userRatingsMatrix)
    # topSimilar = matrixCorr[matrixCorr["nb of ratings"] > 50].head(20)
    
    custom_ratings = [
        [999999, 1, 5],  # Toy Story 1
        [999999, 3114, 5],   # Toy Story 2
        [999999, 4306, 5],   # Shrek 1
        [999999, 6365, 2],   # Matrix Reloaded
        [999999, 858, 0.5],   # The Godfather
        ]
    custom_ratings_df = addRowsToDataframe(userRatings, custom_ratings)
    # model = createModel(custom_df, SVD)
    # topSimilar["prediction"] = topSimilar.apply(lambda row: model.predict(999999, row["movieId"])[3], axis=1)
    # topSimilar.sort_values("prediction", ascending=False, inplace=True)
    topSimilar = getSimilarPredictions(999999, movieTitle, movies, custom_ratings_df, movieRatings, userRatingsMatrix, size=10, minRatings=40)
    print(topSimilar.head(5))