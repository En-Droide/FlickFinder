import pandas as pd
import warnings

from handle_movielens import *


def getMovieCorrelations(movieTitle, movies_df, movieRatings_df, userRatingsMatrix, minRatingAmount):
    movieId = getMovieId(movieTitle, movies_df)
    user_ratings = userRatingsMatrix[movieId]
    similar_to_movie = userRatingsMatrix.corrwith(user_ratings)
    correlatedMovies = pd.DataFrame(similar_to_movie, columns=['Correlation'])
    correlatedMovies.dropna(inplace=True)
    correlatedMovies = correlatedMovies.join(movieRatings_df['nb of ratings'])
    correlatedMovies = correlatedMovies.sort_values('Correlation',
                                                    ascending=False)
    correlatedMovies = correlatedMovies.reset_index(level=["movieId"])
    correlatedMovies["movieTitle"] = correlatedMovies.apply(lambda x: getMovieTitle(x["movieId"], movies_df), axis=1)
    correlatedMovies = correlatedMovies[["movieId", "movieTitle", "Correlation", "nb of ratings"]]
    return correlatedMovies[correlatedMovies["nb of ratings"] > minRatingAmount], similar_to_movie


def getUserCorrelations(userId, movies_df, movieRatings_df, userRatingsMatrix):
    userRatingsMatrix = userRatingsMatrix.T
    user_ratings = userRatingsMatrix[userId]
    similar_to_user = userRatingsMatrix.corrwith(user_ratings)
    correlatedUsers = pd.DataFrame(similar_to_user, columns=['Correlation'])
    correlatedUsers.dropna(inplace=True)
    correlatedUsers = correlatedUsers.sort_values('Correlation',
                                                    ascending=False)
    return correlatedUsers, similar_to_user


def getUserCorrelatedMovies(userList, movies_df, userRatings_df, n):
    correlatedMovies = pd.DataFrame(columns=["movieId", "movieTitle"])
    for user in userList:
        userTopMovies = getUserTopRatings(user, movies_df, userRatings_df, n)[["movieId", "movieTitle"]]
        correlatedMovies = pd.concat([correlatedMovies, userTopMovies])
    return correlatedMovies.drop_duplicates()


if(__name__ == "__main__"):
    warnings.filterwarnings("ignore")
    movies, links, tags, userRatings, movieRatings = readCSVs(resourcePath="csv_files/ml-latest/", ratings_name="ratings.csv", size=100000)
    print("csv read\n")
    print("making MovieMatrix...")
    userRatingsMatrix = getUserRatingsMatrix(userRatings)
    print("movieMatrix done!\n")
    
    movieTitle = 'Matrix, The (1999)'
    movieId = getMovieId(movieTitle, movies)
    matrixCorr, matrixSimilar = getMovieCorrelations(movieTitle, movies, movieRatings, userRatingsMatrix, minRatingAmount=40)
    print("\n\nMovies similar to : " + movieTitle)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(matrixCorr[1:6])
    print("\n")
    
    userId = 10
    matrixCorr2, matrixSimilar2 = getUserCorrelations(userId, movies, movieRatings, userRatingsMatrix)
    
    print("\n\nUsers similar to : " + str(userId))
    print(matrixCorr2.head(10))
    print("\nUser's top ratings : ")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(getUserTopRatings(userId, movies, userRatings, 5))
    for i in range(1, 4):
        print("\nUser", matrixCorr2.iloc[i].name, "top ratings : ")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(getUserTopRatings(matrixCorr2.iloc[i].name, movies, userRatings, 5))
    
    print("Top rated movies from the most similar users :")
    corrList = getUserCorrelatedMovies(matrixCorr2.index[:5], movies, userRatings, 10).sort_values("movieId")
    print(corrList)
