import datetime
import pandas as pd


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


def readCSVs(resourcePath, size):
    movies = readBigCSV(resourcePath + "movies.csv")
    print(" movies df made")
    links = readBigCSV(resourcePath + "links.csv")
    print(" links df made")
    tags = readBigCSV(resourcePath + "tags.csv")
    print(" tags df made")
    userRatings = readRatings(resourcePath + "ratings.csv")[:size]
    print(" userRatings df made")

    movies = movies.set_index("movieId")
    ratingsTemp = pd.merge(userRatings, movies, on='movieId')
    movieRatings = pd.DataFrame(ratingsTemp.groupby('movieId')['rating'].mean()).rename(columns={"rating": "mean rating"})
    movieRatings["nb of ratings"] = pd.DataFrame(
        ratingsTemp.groupby('movieId')['rating'].count())
    return movies, links, tags, userRatings, movieRatings


def getMovieTitle(movieId, movies_df):
    return movies_df.loc[movieId]["title"]


def getMovieId(movieTitle, movies_df):
    return movies_df.index[movies_df["title"] == movieTitle][0]


def getMovieGenres(movieId, movies_df):
    return movies_df.loc[movieId]["genres"]


def getMovieTags(movieId, tags_df):
    return tags_df[tags_df["movieId"] == movieId]


def getMovieImdb(movieId, links_df):
    id = links_df[links_df["movieId"] == movieId]["imdbId"].tolist()[0]
    return str(id).zfill(7)


def getMovieImdbLink(movieId, links_df):
    return "https://www.imdb.com/title/tt" + getMovieImdb(movieId, links_df) + "/"


def getMovieRatings(movieId, ratings_df):
    return ratings_df[ratings_df["movieId"] == movieId]


def convertTimestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


def searchTitle(title: str, movies_df):
    return movies_df[movies_df["title"].str.contains(title, case=False)].drop("genres", axis=1)


def getMovieMatrix(frame):
    movieMat = frame.pivot_table(
        index='userId', columns='movieId', values='rating')
    return movieMat


def addRowsToDataframe(df: pd.DataFrame, new_rows: list):
    return pd.concat([df, pd.DataFrame(data=new_rows, columns=df.columns)])


def read_movielens(path, size):
    movies, links, tags, userRatings, movieRatings =\
        readCSVs(resourcePath=path, size=size)
    return movies, links, tags, userRatings, movieRatings