# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 16:15:21 2023

@author: MatyG
"""
import datetime
import pandas as pd
import numpy as np
from imdb import IMDb

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
    links = readBigCSV(resourcePath + "links.csv")
    # print(links.info(memory_usage='deep'))
    tags = readBigCSV(resourcePath + "tags.csv")
    # print(tags.info(memory_usage='deep'))
    userRatings = readRatings(
        resourcePath + "ratings.csv")
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

file_path = "csv_files/ml-latest-small/movies - Copie.csv"
df = pd.read_csv(file_path)
movies, links, tags, userRatings, ratings, ratingsTemp, ratingsTemp2 =\
    readCSVs(resourcePath="csv_files/ml-latest-small/")
# Create a new column for IMDB ratings
df['keywords'] = ""

def getMovieId(movieTitle):
    return movies.index[movies["title"] == movieTitle][0]

def getMovieImdb(movieId):
    id = links[links["movieId"] == movieId]["imdbId"].tolist()[0]
    return str(id).zfill(7)

title_list = df["title"].tolist()
id_list = [getMovieImdb(getMovieId(title)) for title in title_list]
print(id_list[0])
ia = IMDb()
i =0
for title in title_list[:3]:
    b =ia.search_movie("Toy Story")[0].getID()
    print(ia.get_movie('1825683', info='keywords'))
    print(i)
    # info = ia.search_movie(title)
    get_movie_keywords = ia.get_movie(id_list[i], info='keywords')
    tit = ia.get_movie('0114709')
    print(ia.get_movie('0114709',info='keywords'))
    df.at[i, 'keywords'] = [get_movie_keywords]
    i+=1
    # print(get_movie['keywords'])
