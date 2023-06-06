import datetime
import pandas as pd


def readBigCSV(file):
    mylist = []
    for chunk in pd.read_csv(file, chunksize=20000, encoding='utf8'):
        mylist.append(chunk)
    df = pd.concat(mylist, axis=0)
    return df


def readRatings(file, size):
    mylist = []
    for chunk in pd.read_csv(file, chunksize=20000, encoding='utf8',
                             usecols=["userId", "movieId", "rating"],
                             nrows=size):
        mylist.append(chunk)
    ratings = pd.concat(mylist, axis=0)
    return ratings


def readCSVs(resourcePath, ratings_name, size):
    movies = readBigCSV(resourcePath + "movies.csv")
    print(" movies df made")
    links = readBigCSV(resourcePath + "links.csv")
    # print(" links df made")
    tags = readBigCSV(resourcePath + "tags.csv")
    # print(" tags df made")
    userRatings = readRatings(resourcePath + ratings_name, size)
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


def getMovieRatingsByIndex(movieId, ratings_df):
    return ratings_df.iloc[movieId]


def convertTimestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


def searchTitle(title: str, movies_df):
    return movies_df[movies_df["title"].str.contains(title, case=False)].drop("genres", axis=1)


def getUserRatingsMatrix(frame):
    movieMat = frame.pivot_table(
        index='userId', columns='movieId', values='rating')
    return movieMat


# def addRowsToDataframe(df: pd.DataFrame, new_rows: list):
#     return pd.concat([df, pd.DataFrame(data=new_rows, columns=df.columns)]).reindex(df.index)


def isMovieInDataset(movieTitle, movies_df):
    return len(movies_df[movies_df["title"] == movieTitle]) == 1


def getTopNMoviesByNbOfRatings(n, movies_df, movieRatings_df):
    topMovies = movieRatings_df.sort_values("nb of ratings", ascending=False)[:n]
    topMovies["movieTitle"] = topMovies.apply(lambda row: getMovieTitle(row.name, movies_df), axis=1)
    return topMovies


def getUserTopRatings(userId, movies_df, ratings_df, n):
    topMovies = ratings_df[ratings_df["userId"] == userId].sort_values("rating", ascending=False)[:n]
    topMovies["movieTitle"] = topMovies.apply(lambda row: getMovieTitle(row["movieId"], movies_df), axis=1)
    return topMovies[["userId", "movieId","movieTitle", "rating"]]
    
    
def read_movielens(path, ratings_name, size=999999999999):
    movies, links, tags, userRatings, movieRatings =\
        readCSVs(resourcePath=path, ratings_name=ratings_name, size=size)
    return movies, links, tags, userRatings, movieRatings


if(__name__ == "__main__"):
    movies, links, tags, userRatings, movieRatings = read_movielens(path="csv_files/ml-latest/", ratings_name="ratings.csv", size=1000000)
    print("csv read\n")
    print(userRatings.head(5))
    top = getTopNMoviesByNbOfRatings(10, movies, movieRatings)
    print(top)