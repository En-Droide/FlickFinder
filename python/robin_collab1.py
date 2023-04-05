import datetime
import pandas as pd
import numpy as np

import sys
import warnings
import winerror
import win32api
import win32job

g_hjob = None


def create_job(job_name='', breakaway='silent'):
    hjob = win32job.CreateJobObject(None, job_name)
    if breakaway:
        info = win32job.QueryInformationJobObject(hjob,
                                  win32job.JobObjectExtendedLimitInformation)
        if breakaway == 'silent':
            info['BasicLimitInformation']['LimitFlags'] |= (
                win32job.JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK)
        else:
            info['BasicLimitInformation']['LimitFlags'] |= (
                win32job.JOB_OBJECT_LIMIT_BREAKAWAY_OK)
        win32job.SetInformationJobObject(hjob,
            win32job.JobObjectExtendedLimitInformation, info)
    return hjob


def assign_job(hjob):
    global g_hjob
    hprocess = win32api.GetCurrentProcess()
    try:
        win32job.AssignProcessToJobObject(hjob, hprocess)
        g_hjob = hjob
    except win32job.error as e:
        if (e.winerror != winerror.ERROR_ACCESS_DENIED or
            sys.getwindowsversion() >= (6, 2) or
            not win32job.IsProcessInJob(hprocess, None)):
            raise
        warnings.warn('The process is already in a job. Nested jobs are not '
            'supported prior to Windows 8.')


def limit_memory(memory_limit):
    if g_hjob is None:
        return
    info = win32job.QueryInformationJobObject(g_hjob,
                win32job.JobObjectExtendedLimitInformation)
    info['ProcessMemoryLimit'] = memory_limit
    info['BasicLimitInformation']['LimitFlags'] |= (
        win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY)
    win32job.SetInformationJobObject(g_hjob,
        win32job.JobObjectExtendedLimitInformation, info)

def execLimitMemory(memory=2000):
    assign_job(create_job())
    memory_limit = memory * 1024 * 1024 # memory MiB
    limit_memory(memory_limit)
    try:
        bytearray(memory_limit)
    except MemoryError:
        print('Success: available memory is limited.')
    else:
        print('Failure: available memory is not limited.')
    return 0


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
    id = links[links["movieId"] == movieId]["imdbId"].tolist()[0]
    return str(id).zfill(7)


def getMovieImdbLink(movieId):
    return "https://www.imdb.com/title/tt" + getMovieImdb(movieId) + "/"


def getMovieRatings(movieId):
    return userRatings[userRatings["movieId"] == movieId]


def convertTimestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


movies = movies.set_index("movieId")
tags["datetime"] = tags["timestamp"].apply(convertTimestamp)
userRatings["datetime"] = userRatings["timestamp"].apply(convertTimestamp)

ratingsTemp = pd.merge(userRatings, movies, on='movieId')
ratings = pd.DataFrame(ratingsTemp.groupby('title')['rating'].mean())

ratings["nb of ratings"] = pd.DataFrame(
    ratingsTemp.groupby('title')['rating'].count())

ratingsTemp2 = ratingsTemp[["userId", "movieId", "rating"]]


def getCustomMovieMat(frame, column):
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


def getMovieMat(frame):
    movieMat = frame.pivot_table(
        index='userId', columns='movieId', values='rating')
    return movieMat


def getCorrelations(movieId=None, movieTitle=None):
    if movieTitle and not movieId:
        movieId = getMovieId(movieTitle)
    if not movieTitle:
        movieTitle = getMovieTitle(movieId)
    movieMat = ratingsTemp.pivot_table(
        index='userId', columns='title', values='rating')
    user_ratings = movieMat[movieTitle]
    similar_to_movie = movieMat.corrwith(user_ratings)
    correlatedMovies = pd.DataFrame(similar_to_movie, columns=['Correlation'])
    correlatedMovies.dropna(inplace=True)
    correlatedMovies = correlatedMovies.join(ratings['nb of ratings'])
    correlatedMovies = correlatedMovies.sort_values('Correlation',
                                                    ascending=False)
    return correlatedMovies, similar_to_movie, user_ratings, movieMat


def getCorrelations2(movieId=None, movieTitle=None, movieMat=None):
    if movieTitle and not movieId:
        movieId = getMovieId(movieTitle)
    if not movieTitle:
        movieTitle = getMovieTitle(movieId)
    if movieMat is None:
        movieMat = getMovieMat(ratingsTemp2)
    user_ratings = movieMat[movieId]
    similar_to_movie = movieMat.corrwith(user_ratings)
    correlatedMovies = pd.DataFrame(similar_to_movie, columns=['Correlation'])
    correlatedMovies.dropna(inplace=True)
    correlatedMovies.index = correlatedMovies.index.map(getMovieTitle)
    correlatedMovies = correlatedMovies.join(ratings['nb of ratings'])
    correlatedMovies = correlatedMovies.sort_values('Correlation',
                                                    ascending=False)
    return correlatedMovies, similar_to_movie, user_ratings, movieMat


# execLimitMemory(3000)  # 2000 MiB

pivoted = getCustomMovieMat(ratingsTemp, column="movieId")

matrixCorr, matrixSimilar, usrat, movieMat = getCorrelations2(
    movieTitle='Matrix, The (1999)', movieMat=None)
print(matrixCorr[matrixCorr["nb of ratings"] > 50].head(10))
