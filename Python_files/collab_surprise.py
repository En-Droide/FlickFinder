import datetime
import pandas as pd
import numpy as np
from imdb import Cinemagoer
import sys
import warnings
from tqdm import tqdm
from tqdm.contrib import itertools
import os
from surprise import accuracy, Dataset, Reader, SVD, KNNBasic, KNNWithMeans, SVDpp, SlopeOne
from surprise.model_selection import train_test_split, cross_validate

from handle_movielens import *


def createModel(df: pd.DataFrame, model):
    reader = Reader(rating_scale=(0.5, 5.0))
    print("reader done")
    data = Dataset.load_from_df(df, reader)
    print("data done")
    algo = model()
    print("algo created")
    trainset = data.build_full_trainset()
    algo.fit(trainset)
    # cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=3)
    print("fit done")
    return algo


def predictAllUserRatings(df: pd.DataFrame, model, userId: int):
    movieTitles = df["movieId"].unique()
    new_rows = []
    print("\nPredicting...")
    for movieId in tqdm(movieTitles):
        rating = df[(df["userId"] == userId) & 
                                       (df["movieId"] == movieId)]["rating"]
        if rating.empty:
            new_rows.append([userId, movieId, model.predict(userId, movieId)[3]])
    return new_rows


def getPredictedRatings(old_df: pd.DataFrame, new_df: pd.DataFrame, userId: int):
    predictedRatings = new_df[~(new_df["movieId"].isin(old_df[old_df["userId"] == userId]["movieId"].values)) & (new_df["userId"] == userId)].sort_values("movieId")
    return predictedRatings


def getTopRatings(df: pd.DataFrame, userId: int, nb: int, thresh: float, minCount: int):
    ratingsWithCounts = df.merge(movieRatings, left_on="movieId", right_index=True)
    ratingsWithCounts = ratingsWithCounts[ratingsWithCounts["nb of ratings"] >= minCount]
    result = ratingsWithCounts[(ratingsWithCounts["userId"] == userId) & (ratingsWithCounts["rating"] >= thresh)].sort_values("rating", ascending=False)[: nb]
    return result


def getTopRatingsByCount(df: pd.DataFrame, userId: int, nb: int, thresh: float, minCount: int):
    ratingsWithCounts = df.merge(movieRatings, left_on="movieId", right_index=True)
    ratingsWithCounts = ratingsWithCounts[ratingsWithCounts["nb of ratings"] >= minCount]
    result = ratingsWithCounts[(ratingsWithCounts["userId"] == userId) & (ratingsWithCounts["rating"] >= thresh)].sort_values(["rating", "nb of ratings"], ascending=[False, False])[: nb]
    return result


def getRecommandations(userId: int, movies_df: pd.DataFrame, ratings_df: pd.DataFrame, nb_results: int, thresh: float, minCount: int):
    model = createModel(ratings_df, SVD)
    preds = predictAllUserRatings(ratings_df, model, userId)
    print("predictions done")
    new_ratings = addRowsToDataframe(ratings_df, preds)
    print("new predicted ratings added")
    pred_ratings = getPredictedRatings(ratings_df, new_ratings, userId)
    pred_ratings["title"] = pred_ratings["movieId"].apply(lambda id: getMovieTitle(movieId=id, movies_df=movies_df))
    top10 = getTopRatings(pred_ratings, userId, nb_results, thresh, minCount)
    top10Weighted = getTopRatingsByCount(pred_ratings, userId, nb_results, thresh, minCount)
    result = top10  # top10 or top10Weighted
    print("top 10 :\n", result[["movieId", "title", "rating"]])
    return preds, pred_ratings, top10, top10Weighted


if(__name__ == "__main__"):
    movies, links, tags, userRatings, movieRatings = readCSVs(resourcePath="csv_files/ml-latest/", size=1000000)
    print("csv read\n")
    
    custom_ratings = [
        [999999, 1, 5],  # Toy Story 1
        [999999, 3114, 5],   # Toy Story 2
        [999999, 4306, 5],   # Shrek 1
        # [999999, 6365, 0.5],   # Matrix Reloaded
        # [999999, 858, 0.5],   # The Godfather
        ]
    custom_df = addRowsToDataframe(userRatings, custom_ratings)
    print("custom ratings added")
    preds, pred_ratings, top10, top10Weighted = getRecommandations(userId=999999, movies_df= movies, ratings_df=custom_df, nb_results=10, thresh=0, minCount=5)
    print("\n\n", pred_ratings["rating"].describe())
