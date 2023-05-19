import datetime
import pandas as pd
import numpy as np
from imdb import Cinemagoer
import sys
import warnings
from tqdm import tqdm
import os

movies = None
links = None
tags = None
userRatings = None
ratings = None
ratingsTemp = None
ratingsTemp2 = None


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
    df = pd.concat(mylist, axis=0)
    return df


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
    userRatings = readRatings(resourcePath + "ratings.csv")
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


def getInfos(movieId):
    try:
        imdbId = getMovieImdb(movieId)
        ia = Cinemagoer()
        # print(ia.get_movie_infoset())
        movie = ia.get_movie(imdbId , info=["keywords", "main"])  #
        # print(movie.infoset2keys)
        # print(movie.current_info)
        # print(movie.get("main"))
        keywords = movie["keywords"]
        # print(keywords, "\n\n")
        # print(movie["relevant keywords"])
        # synopsis = movie.get("plot")
        cast = movie["cast"]
    except:
        keywords = ["_error"]
        cast = ["_error"]
    return keywords, cast

movies, links, tags, userRatings, ratings, ratingsTemp, ratingsTemp2 =\
    readCSVs(resourcePath="csv_files/ml-latest-small/")
print("csv read")

movies["keywords"] = ''
movies["cast"] = ''
for i in tqdm(movies.index):  # 
    # print(i, "/", len(movies))
    keywords, cast = getInfos(i)
    movies.at[i, "keywords"] = keywords
    if "_error" not in cast:
        cast = [actor["name"] for actor in cast]
    movies.at[i, "cast"] = cast
movies.to_csv("out.csv")
