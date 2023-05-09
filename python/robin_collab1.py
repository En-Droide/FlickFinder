import datetime
import pandas as pd
import numpy as np
from imdb import Cinemagoer
import sys
import warnings
from tqdm import tqdm
import os
import surprise

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

"""
def getCustomMovieMat_test(frame, chunk_size, file_path):
    # if not os.path.exists(file_path):
    # print(pd.read_hdf("store.h5").dtypes)
    store = pd.HDFStore("store.h5")
    chunker = [frame[i:i+chunk_size] for i in range(0,frame.shape[0],chunk_size)]  # pd.read_csv(file_path, chunksize=chunk_size)
    for i in tqdm(range(0, len(chunker) - 1)):
        # print(i)
        dummy = pd.DataFrame()
        dummy["movieId"] = np.sort(userRatings["movieId"].unique())
        dummy["userId"] = 0
        dummy["rating"] = 0
        # print(dummy)
        chunker[i] = pd.concat([chunker[i], dummy])
        data=chunker[i].pivot_table(values='rating',
                                    index='userId',
                                    columns="movieId",
                                    fill_value=0).reset_index()
        data.columns = data.columns.astype(np.int)
        print(data.info)
        store.append("df", data)
    df = store["df"]
    df.to_csv(file_path)
    store.close()
    return pd.read_csv(file_path, index_col="userId")


def pivotSegment(segmentNumber, passedFrame, segmentSize):
    pass


def getCustomMovieMat(frame, chunk_size, file_path):
    # if not os.path.exists(file_path):
        chunker = [frame[i:i+chunk_size] for i in range(0,frame.shape[0],chunk_size)]  # pd.read_csv(file_path, chunksize=chunk_size)
        store = pd.HDFStore("store.h5")
        for i in tqdm(range(0, len(chunker) - 1)):
            data = chunker[i].pivot('userId', 'movieId', 'rating')
            print(data)
            store.append("df", data)
        store.close()
        
        
def getCustomMovieMat2(frame, chunk_size, file_path):
    ratings = pd.read_csv(file_path,
                          usecols=["userId", "movieId", "rating"],
                          chunksize=50000,
                          dtype={"movieId": np.int64,
                                 "rating": np.float64,
                                 "userId": np.int64})
    store = pd.HDFStore("store2.h5", mode="w")
    for chunk in ratings:
        data = chunk.pivot(index='userId', columns='movieId', values='rating')
        print(data.dtypes)
        data.columns = data.columns.astype(np.int64)
        store.append("pivot", data)
    store.close()


def getCustomMovieMat_memoryloss(frame, chunk_size, file_path):  # seems fine, slows gradually and memory dies at 60%
    chunker = [frame[i:i+chunk_size] for i in range(0, frame.shape[0], chunk_size)]  # pd.read_csv(file_path, chunksize=chunk_size)
    tot=pd.DataFrame()
    for i in tqdm(range(0, len(chunker) - 1)):
        tot=tot.add(chunker[i].pivot(index='userId', columns='movieId', values='rating'), fill_value=0)
    tot.to_csv(file_path)
    return tot
"""

def getMovieCorrelations(movieId=None, movieTitle=None, customPivot=False, file_path="small_pivotTable.csv"):
    if movieTitle and not movieId:
        movieId = getMovieId(movieTitle)
    if not movieTitle:
        movieTitle = getMovieTitle(movieId)
    # if customPivot:
    #     movieMat = getCustomMovieMat_memoryloss(userRatings, 5000, file_path)
    # else:
    movieMat = getMovieMat(userRatings)
    movieMat.columns = movieMat.columns.astype("int64")
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



def find_correlation_between_two_users(movieMat: pd.DataFrame, user1: str, user2: str):
    """Find correlation between two users based on their rated movies using Pearson correlation"""
    rated_movies_by_both = movieMat.loc[[user1, user2]].dropna(axis=1).T
    print(rated_movies_by_both.corr())
    user1_ratings = rated_movies_by_both.iloc[0]
    user2_ratings = rated_movies_by_both.iloc[1]
    print(np.corrcoef(user1_ratings.tolist(), user2_ratings.tolist()))
    # print(user1_ratings.corrwith(user2_ratings))
    # return np.corrcoef(user1_ratings, user2_ratings)[0, 1]
    # return pd.Series(user1_ratings).corr(pd.Series(user2_ratings))
    return rated_movies_by_both.corr().at[0, 1]


movies, links, tags, userRatings, ratings, ratingsTemp, ratingsTemp2 =\
    readCSVs(resourcePath="csv_files/ml-latest-small/")
print("csv read")
# movmat = pd.read_csv("full_pivotTable.csv", index_col="userId")  # getCustomMovieMat_test(ratingsTemp, 10000, "full_pivotTable.csv")
# getCustomMovieMat2(userRatings, 10000, "csv_files/ml-latest-small/ratings.csv")
# movmat = pd.read_hdf("store2.h5")
# print(pd.read_hdf("store.h5").dtypes)
matrixCorr, matrixSimilar, usrat, movieMat = getMovieCorrelations(
    movieTitle='Toy Story (1995)', customPivot=False, file_path="small_pivotTable.csv")
print(matrixCorr[matrixCorr["nb of ratings"] > 50].head(10))
print("\n")
# print(find_correlation_between_two_users(movieMat, 1, 2))
users = userRatings["userId"].unique()
# similarity_matrix = np.empty((len(users), len(users)), dtype=float)
# for user1 in tqdm(users, desc='user1', position=0):
#     for user2 in tqdm(users, desc='user2', position=1):
#         similarity_matrix += find_correlation_between_two_users(movieMat, user1, user2)
# # similarity_matrix = np.array([[find_correlation_between_two_users(movieMat, user1, user2) for user1 in users] for user2 in users])
# similarity_df = pd.DataFrame(similarity_matrix, columns=users, index=users)
# print(similarity_df)
# surprise.similarities.pearson(len(users), )
