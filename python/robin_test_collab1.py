import time, datetime, json
import selenium
from selenium import webdriver
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# driver = webdriver.Edge()
# driver.get("https://www.imdb.com/title/tt0112302/")
resourcePath = "ml-latest-small/"
movies = pd.read_csv(resourcePath + "movies.csv", encoding='utf8')
links = pd.read_csv(resourcePath + "links.csv", encoding='utf8')
tags = pd.read_csv(resourcePath + "tags.csv", encoding='utf8')
userRatings = pd.read_csv(resourcePath + "ratings.csv", encoding='utf8')


def getMovieTitle(movieId):
    return movies.loc[movieId]["title"]


def getMovieId(movieTitle):
    return movies.index[movies["title"] == movieTitle][0]


def getMovieGenres(movieId):
    return movies.loc[movieId]["genres"]


def getMovieTags(movieId):
    return tags[tags["movieId"] == movieId]


def getMovieImdb(movieId):
    id = links[links["movieId"] == movieId]["imdbId"][0]
    return str(id).zfill(7)


def getMovieImdbLink(movieId):
    return "https://www.imdb.com/title/tt" + getMovieImdb(movieId) + "/"


def getMovieRatings(movieId):
    return userRatings[userRatings["movieId"] == movieId]


def convertTimestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


movies = movies.set_index("movieId")
# print("Number of movies :", movies.size)
tags["datetime"] = tags["timestamp"].apply(convertTimestamp)
userRatings["datetime"] = userRatings["timestamp"].apply(convertTimestamp)

ratingsTemp = pd.merge(userRatings, movies, on='movieId')
ratings = pd.DataFrame(ratingsTemp.groupby('title')['rating'].mean())

ratings["nb of ratings"] = pd.DataFrame(
    ratingsTemp.groupby('title')['rating'].count())

plt.figure(figsize=(8, 4))
ratings['nb of ratings'].hist(bins=80, log=True)
plt.xlabel("Amount of ratings")
plt.ylabel("Amount of movies")
# plt.show()

plt.figure(figsize=(8, 4))
ratings['rating'].hist(bins=80)
plt.xlabel("Rating")
plt.ylabel("Amount of movies")
# plt.show()

movieMatrix = ratingsTemp.pivot_table(
    index='userId', columns='title', values='rating')

# print(ratings.sort_values('nb of ratings', ascending=False).head(10))
"""
forrest_user_ratings = movieMatrix['Forrest Gump (1994)']
matrix_user_ratings = movieMatrix['Matrix, The (1999)']
similar_to_forrest = movieMatrix.corrwith(forrest_user_ratings)
similar_to_matrix = movieMatrix.corrwith(matrix_user_ratings)

corr_forrest = pd.DataFrame(similar_to_forrest, columns=['Correlation'])
corr_forrest.dropna(inplace=True)
# print(corr_forrest.sort_values('Correlation', ascending=False).head(10))
corr_forrest = corr_forrest.join(ratings['nb of ratings'])

# print(corr_forrest.head())

# print(corr_forrest[corr_forrest['nb of ratings'] > 100]
#       .sort_values('Correlation', ascending=False).head())

corr_matrix = pd.DataFrame(similar_to_matrix, columns=['Correlation'])
corr_matrix.dropna(inplace=True)
# print(corr_matrix.sort_values('Correlation', ascending=False).head(10))
corr_matrix = corr_matrix.join(ratings['nb of ratings'])

# print(corr_matrix.head())

# print(corr_matrix[corr_matrix['nb of ratings'] > 100]
#        .sort_values('Correlation', ascending=False).head())
"""

def getCorrelations(movieId=None, movieTitle=None):
    if movieTitle and not movieId:
        movieId = getMovieId(movieTitle)
    user_ratings = movieMatrix[getMovieTitle(movieId)]
    similar_to_movie = movieMatrix.corrwith(user_ratings)
    correlatedMovies = pd.DataFrame(similar_to_movie, columns=['Correlation'])
    correlatedMovies.dropna(inplace=True)
    correlatedMovies = correlatedMovies.join(ratings['nb of ratings'])
    correlatedMovies = correlatedMovies.sort_values('Correlation', ascending=False)
    return correlatedMovies, similar_to_movie


matrixCorr, matrixSimilar = getCorrelations(movieTitle='Matrix, The (1999)')
print(matrixCorr[matrixCorr["nb of ratings"] > 30].head())
