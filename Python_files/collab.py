# -*- coding: utf-8 -*-
"""
Created on Sat May 20 12:31:30 2023

@author: lotod
"""

from handle_movielens import *
from collab_surprise import *
from collab_similarities import *


def getMovieSimilarPredictions(userId, movieTitle, movies_df, movieRatings_df, userRatingsMatrix, model, size, minRatings):
    matrixCorr, matrixSimilar = getMovieCorrelations(movieTitle, movies_df, movieRatings_df, userRatingsMatrix, minRatings)
    topSimilar = matrixCorr[matrixCorr["nb of ratings"] >= minRatings].head(size)
    topSimilar["prediction"] = topSimilar.apply(lambda row: model.predict(userId, row["movieId"])[3], axis=1)
    topSimilar.sort_values("prediction", ascending=False, inplace=True)
    return topSimilar.drop("nb of ratings", axis=1)


def getUserSimilarPredictions(userId, movies_df, userRatings_df, movieRatings_df, userRatingsMatrix, model, userAmount, ratingsPerUser):
    matrixCorr, matrixSimilar = getUserCorrelations(userId, movies_df, movieRatings_df, userRatingsMatrix)    
    correlatedMovies = getUserCorrelatedMovies(matrixCorr.index[:userAmount], movies_df, userRatings_df, ratingsPerUser)
    moviesRatedByUser = userRatings_df[userRatings_df["userId"] == userId]["movieId"].values
    correlatedMovies = correlatedMovies[~correlatedMovies["movieId"].isin(moviesRatedByUser)]
    correlatedMovies["prediction"] = correlatedMovies.apply(lambda row: model.predict(userId, row["movieId"])[3], axis=1)
    correlatedMovies.sort_values("prediction", ascending=False, inplace=True)
    return correlatedMovies

if(__name__ == "__main__"):
    movies, links, tags, userRatings, movieRatings = readCSVs(resourcePath="csv_files/ml-latest/", ratings_name="ratings.csv", size=100000)
    print("csv read\n")
    print("making MovieMatrix...")
    print("movieMatrix done!\n")
    movieTitle = 'Shrek 2 (2004)'
    # movieId = getMovieId(movieTitle, movies)
    
    custom_ratings = pd.DataFrame(data=[
        [999999, 1, 5],  # Toy Story 1
        [999999, 3114, 5],   # Toy Story 2
        [999999, 4306, 5],   # Shrek 1
        [999999, 6365, 2],   # Matrix Reloaded
        [999999, 858, 0.5],   # The Godfather
        ], columns=userRatings.columns)
    userRatings = pd.concat([userRatings, custom_ratings])
    userRatingsMatrix = getUserRatingsMatrix(userRatings)
    
    model = createModel(userRatings, SVD)
    
    print("\ndoing similar movies prediction...")
    topSimilar = getMovieSimilarPredictions(999999, movieTitle, movies, movieRatings, userRatingsMatrix, model, 20, 40)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(topSimilar.head(10))
    
    print("\ndoing similar user prediction...")
    topSimilar2 = getUserSimilarPredictions(999999, movies, userRatings, movieRatings, userRatingsMatrix, model, 10, 10)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(topSimilar2.head(10))