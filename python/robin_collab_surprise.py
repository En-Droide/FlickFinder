import datetime
import pandas as pd
import numpy as np
from imdb import Cinemagoer
import sys
import warnings
from tqdm import tqdm
from tqdm.contrib import itertools
import os
from surprise import accuracy, Dataset, SVD, Reader, KNNBasic
from surprise.model_selection import train_test_split, cross_validate

movies = None
links = None
tags = None
userRatings = None
ratings = None
ratingsTemp = None
ratingsTemp2 = None
pd.set_option('io.hdf.default_format', 'table')


def readBigCSV(file):
    mylist = []
    for chunk in pd.read_csv(file, chunksize=20000, encoding='utf8'):
        mylist.append(chunk)
    df = pd.concat(mylist, axis=0)
    return df


def readRatings(file):
    mylist = []
    for chunk in pd.read_csv(file, chunksize=20000, encoding='utf8',
                             usecols=["userId", "movieId", "rating"]):
        mylist.append(chunk)
    ratings = pd.concat(mylist, axis=0)
    return ratings


def readCSVs(resourcePath="csv_files/ml-latest-small/"):
    movies = readBigCSV(resourcePath + "movies.csv")
    # print(movies.info(memory_usage='deep'))
    print("movies df made")
    links = readBigCSV(resourcePath + "links.csv")
    print("links df made")
    # print(links.info(memory_usage='deep'))
    tags = readBigCSV(resourcePath + "tags.csv")
    # print(tags.info(memory_usage='deep'))
    print("userRatings df made")
    # print(userRatings.info(memory_usage='deep'))

    movies = movies.set_index("movieId")
    # tags["datetime"] = tags["timestamp"].apply(convertTimestamp)
    # userRatings["datetime"] = userRatings["timestamp"].apply(convertTimestamp)

    ratingsTemp = pd.merge(userRatings, movies, on='movieId')
    ratings = pd.DataFrame(ratingsTemp.groupby('title')['rating'].mean())

    ratings["nb of ratings"] = pd.DataFrame(
        ratingsTemp.groupby('title')['rating'].count())

    ratingsTemp2 = ratingsTemp[["userId", "movieId", "rating"]]
    return movies, links, tags, userRatings, ratings, ratingsTemp, ratingsTemp2


def getMovieTitle(movieId):
    return movies.loc[movieId]["title"]


def getMovieId(movieTitle):
    return movies.index[movies["title"] == movieTitle][0]


def getMovieGenres(movieId):
    return movies.loc[movieId]["genres"]


def getMovieTags(movieId):
    return tags[tags["movieId"] == movieId]


def getMovieImdb(movieId):
    id = links[links["movieId"] == movieId]["imdbId"].tolist()[0]
    return str(id).zfill(7)


def getMovieImdbLink(movieId):
    return "https://www.imdb.com/title/tt" + getMovieImdb(movieId) + "/"


def getMovieRatings(movieId):
    return userRatings[userRatings["movieId"] == movieId]


def convertTimestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


def searchTitle(title: str):
    return movies[movies["title"].str.contains(title, case=False)].drop("genres", axis=1)


def getMovieMat(frame):
    movieMat = frame.pivot_table(
        index='userId', columns='movieId', values='rating')
    return movieMat


def addRowsToDataframe(df: pd.DataFrame, new_rows: list):
    return pd.concat([df, pd.DataFrame(data=new_rows, columns=df.columns)])


def predictRatings(df: pd.DataFrame, userId: int):
    reader = Reader(rating_scale=(0.5, 5.0))
    print("reader done")
    data = Dataset.load_from_df(df, reader)
    print("data done")
    algo = SVD(verbose=True)
    print("algo created")
    trainset = data.build_full_trainset()
    algo.fit(trainset)
    # cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=3)
    print("fit done")
    movieTitles = df["movieId"].unique()
    new_rows = []
    print("\nPredicting...")
    for movieId in tqdm(movieTitles):
        rating = df[(df["userId"] == userId) & 
                                       (df["movieId"] == movieId)]["rating"]
        if rating.empty:
            new_rows.append([userId, movieId, algo.predict(userId, movieId)[3]])
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


def getRecommandations(userId: int, ratings_df: pd.DataFrame, nb_results: int, thresh: float, minCount: int):
    preds = predictRatings(ratings_df, userId)
    print("predictions done")
    new_ratings = addRowsToDataframe(ratings_df, preds)
    print("new predicted ratings added")
    pred_ratings = getPredictedRatings(ratings_df, new_ratings, userId)
    pred_ratings["title"] = pred_ratings["movieId"].map(getMovieTitle)
    top10 = getTopRatings(pred_ratings, userId, nb_results, thresh, minCount)
    top10Weighted = getTopRatingsByCount(pred_ratings, userId, nb_results, thresh, minCount)
    result = top10  # top10 or top10Weighted
    print("top 10 :\n", result[["movieId", "title", "rating"]])
    return preds, pred_ratings, top10, top10Weighted


movies, links, tags, userRatings, movieRatings =\
    readCSVs(resourcePath="csv_files/ml-latest/", size=1000000)
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
preds, pred_ratings, top10, top10Weighted = getRecommandations(userId=999999, ratings_df=custom_df, nb_results=10, thresh=0, minCount=5)
print("\n\n", pred_ratings["rating"].describe())
