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
    print("movies df made")
    # print(tags.info(memory_usage='deep'))
    userRatings= readRatings(resourcePath + "ratings.csv")
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


def getMovieMat(frame):
    movieMat = frame.pivot_table(
        index='userId', columns='movieId', values='rating')
    return movieMat



movies, links, tags, userRatings, ratings, ratingsTemp, ratingsTemp2 =\
    readCSVs(resourcePath="csv_files/ml-latest-small/")
print("csv read")

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(userRatings, reader)

algo = SVD()
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=3)
print("\nSVD done\n")
userRatings_pred = userRatings
# userId = input("enter user id : ")
# userId = 1
users = userRatings["userId"].unique()
movies = userRatings["movieId"].unique()
new_rows = []
with tqdm(total=len(users) * len(movies)) as pbar:
    for userId in users:
        for movieId in movies:
            # print("movie " + str(movieId))
            rating = userRatings_pred[(userRatings_pred["userId"] == userId) & 
                                           (userRatings_pred["movieId"] == movieId)]["rating"]
            # print(rating)
            if rating.empty:
                new_rows.append([userId, movieId, algo.predict(userId, movieId)[3]])
            pbar.update(1)
userRatings_pred = pd.concat([userRatings_pred, pd.DataFrame(data=new_rows, columns=userRatings_pred.columns)])
userRatings_pred.to_csv("ratings_predicted.csv")