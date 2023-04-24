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


def getCustomMovieMat_old(frame, column):
    pivoted_table = pd.DataFrame(index=np.sort(frame["userId"].unique()),
                                 columns=np.sort(frame["movieId"].unique()),
                                 dtype=np.float64)
    # pivoted_table = pivoted_table.astype(np.float64)
    if column == "title":
        pivoted_table.columns = frame["title"].unique()
    for user in frame["userId"].unique():
        for index, rating in frame[frame["userId"] == user].iterrows():
            pivoted_table.loc[user][rating["movieId"]] = rating["rating"]
    return pivoted_table


def getCustomMovieMat_test(frame, chunk_size, file_path):
    chunker = [frame[i:i+chunk_size] for i in range(0,frame.shape[0],chunk_size)]  # pd.read_csv(file_path, chunksize=chunk_size)
    tot=pd.DataFrame()
    for i in tqdm(range(0, len(chunker) - 1)):
        tot=tot.add(chunker[i].pivot('userId', 'movieId', 'rating'), fill_value=0)
    tot.to_csv(file_path)
    return pd.read_csv(file_path)


def getCustomMovieMat(frame, chunk_size, file_path):
    chunks = [x for x in range(0, frame.shape[0], chunk_size)]
    
    # for i in range(0, len(chunks) - 1):
    #     print(chunks[i], chunks[i + 1] - 1)
    print("\nCustom Pivot Table : created", len(chunks), "chunks")
    # pivot_df = pd.DataFrame()
    if os.path.exists(file_path):
        os.remove(file_path)
    for i in tqdm(range(0, len(chunks) - 1)):
        print(chunks[i], ":", chunks[i + 1] - 1)
        chunk_df = frame.iloc[chunks[i]:chunks[i + 1] - 1]
        interactions = (
        chunk_df.groupby(["userId", "title"])["rating"]
        .sum()
        .unstack()
        .reset_index()
        .fillna(0)
        .set_index("userId")
        )
        print("\n\n",interactions.columns)
        interactions.to_csv(file_path+str(i)+".csv", mode="a", index=False, header=not os.path.exists(file_path))
        # print (interactions.shape)
        # pivot_df = pd.concat([pivot_df, interactions], axis=0, join='outer') 
    # return pd.read_csv(file_path, sep=",", index_col="userId")
    

def getCorrelations(movieId=None, movieTitle=None, customPivot=False):
    if movieTitle and not movieId:
        movieId = getMovieId(movieTitle)
    if not movieTitle:
        movieTitle = getMovieTitle(movieId)
    if customPivot:
        movieMat = getCustomMovieMat(ratingsTemp, 10000, "full_pivotTable")
    else:
        movieMat = getMovieMat(ratingsTemp)
    print("\nMovieMat made")
    user_ratings = movieMat[movieId]
    similar_to_movie = movieMat.corrwith(user_ratings)
    correlatedMovies = pd.DataFrame(similar_to_movie, columns=['Correlation'])
    correlatedMovies.dropna(inplace=True)
    correlatedMovies.index = correlatedMovies.index.map(getMovieTitle)
    correlatedMovies = correlatedMovies.join(ratings['nb of ratings'])
    correlatedMovies = correlatedMovies.sort_values('Correlation',
                                                    ascending=False)
    return correlatedMovies, similar_to_movie, user_ratings, movieMat


movies, links, tags, userRatings, ratings, ratingsTemp, ratingsTemp2 =\
    readCSVs(resourcePath="csv_files/ml-latest/")
print("csv read")
movmat = getCustomMovieMat_test(ratingsTemp, 10000, "full_pivotTable.csv")
# getCustomMovieMat(ratingsTemp, 10000, "full_pivotTable.csv")
# matrixCorr, matrixSimilar, usrat, movieMat = getCorrelations(
#     movieTitle='Matrix, The (1999)', customPivot=True)
# print(matrixCorr[matrixCorr["nb of ratings"] > 50].head(10))

# testdf = ratingsTemp[["userId", "movieId", "rating"]]
# testdf = testdf.set_index("userId").stack(level=0)

