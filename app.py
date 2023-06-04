from flask import Flask, render_template, request, abort
import logging
import os
import sys
import pandas as pd

project_path = "C:\\Users\\lotod\\OneDrive\\Bureau\\GIT\\FlickFinder\\"
# project_path = "C:\\Users\\lotod\\Desktop\\GIT\\FlickFinder\\"
# project_path = "C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\"

is_setup_tfidf_onStart = True
is_handle_movielens_onStart = True
is_getMovieMatrix_onStart = True
is_setup_recommendation_model_onStart = True
is_create_main_onStart = True
is_setup_movie_informations = True

instance_path = project_path
templates_path = instance_path + "templates\\"
images_path = instance_path + "static\\Images\\"
python_path = instance_path + "Python_files\\"
sys.path.insert(1, python_path)
movieLens_path = python_path + "csv_files\\ml-latest\\"
rating_path = movieLens_path + "ratings.csv"
outBigData_path = python_path + "csv_files\\out_big_data.csv"
info_movie_path_csv = project_path + "static\\Csv_files\\movies_informations.csv"

from handle_movielens import *
from tfidf import start_tfidf, setup_tfidf, get_movie_genres_cast, match_title
from collab import *
from collab_similarities import getMovieCorrelations
from create_pages import *
from scrap import *

currentUserId = None
currentUserRatings = None

app = Flask(__name__, instance_path=instance_path)
app.config["TEMPLATES_AUTO_RELOAD"] = True
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/")
def home():
    return render_template("main.html", currentUserId=currentUserId)

@app.route("/main.html")
def main():
    return render_template("main.html", currentUserId=currentUserId)

@app.route("/account.html")
def account():
    return render_template("account.html", currentUserId=currentUserId)

@app.route("/_tfidf", methods=["POST"])
def createPage():
    movieTitle = request.form.get("searchText")
    tfidf_movieFilmList = start_tfidf(tfidf_df, tfidf_matrix, movieTitle, size=7)
    print("tfidf : \n", tfidf_movieFilmList, "\n")
    similarity_movieFilmList = getMovieCorrelations(tfidf_movieFilmList[0], movies_df, movieRatings_df, userRatingsMatrix, minRatingAmount=50)[0]["movieTitle"].to_list()[:8]
    print("similarity : \n", similarity_movieFilmList, "\n")
    global failed_scraps
    soup = None
    for movie in (tfidf_movieFilmList[:4] + similarity_movieFilmList[:4]):
        if not(os.path.exists(images_path + "scrap\\" + movie + ".jpg") or movie in failed_scraps):
            movieId = getMovieId(movie, movies_df)
            movieLink = getMovieImdbLink(movieId, links_df)
            print(movieLink)
            soup = request_soup(movieLink)
            response = scrap_image(soup, images_path=images_path, movieTitle=movie)
            if response == "ERROR_IMAGE": failed_scraps += [movieTitle]
            
        if movie not in df_movie_info['title'].values:
            movieId = getMovieId(movie, movies_df)
            movieLink = getMovieImdbLink(movieId, links_df)
            print(movieLink)
            soup = request_soup(movieLink)
            scrape_and_create_movie_csv(info_movie_path_csv,soup, movie)
    SimilarPageCreation(tfidf_movies=tfidf_movieFilmList,
                        similarity_movies=similarity_movieFilmList,
                        file_path=templates_path + "similar_movies.html",
                        images_path=images_path, row_size=4)
    return "Done!"

@app.route('/similar_movies.html')
def similar_movies():
    return render_template('similar_movies.html', currentUserId=currentUserId)

@app.route('/_movie/<movieTitle>')
def movie_page(movieTitle):
    print("movie: ", movieTitle)
    if not(isMovieInDataset(movieTitle, movies_df)):
        abort(404)
    list_movie_genres, list_movie_cast = get_movie_genres_cast(tfidf_df, movieTitle)
    movieId = getMovieId(movieTitle=movieTitle, movies_df=tfidf_df)
    try:
        mean_rating_movie = round(getMovieRatingsByIndex(movieId, movieRatings_df)["mean rating"], 1)
    except IndexError:
        print("ERROR : no ratings found in current sample")
        mean_rating_movie = "error"
    movieTitle = movieTitle.replace("'", "&quot;")
    df_movie_info = pd.read_csv(info_movie_path_csv)    
    informations_movieDate, informations_movieTime, informations_movieSynopsis, informations_movieDirector = informations_movies (movieTitle, df_movie_info)

    similarity_movieFilmList = getMovieCorrelations(movieTitle, movies_df, movieRatings_df, userRatingsMatrix, minRatingAmount=50)[0]["movieTitle"].to_list()[1:6]
    print("similarity : \n", similarity_movieFilmList, "\n")
    global failed_scraps
    soup = None
    for movie in (similarity_movieFilmList):
        if not(os.path.exists(images_path + "scrap\\" + movie + ".jpg") or movie in failed_scraps):
            movieId = getMovieId(movie, movies_df)
            movieLink = getMovieImdbLink(movieId, links_df)
            print(movieLink)
            soup = request_soup(movieLink)
            response = scrap_image(soup, images_path=images_path, movieTitle=movie)
            if response == "ERROR_IMAGE": failed_scraps += [movieTitle]
            
        if movie not in df_movie_info['title'].values:
            movieId = getMovieId(movie, movies_df)
            movieLink = getMovieImdbLink(movieId, links_df)
            print(movieLink)
            soup = request_soup(movieLink)
            scrape_and_create_movie_csv(info_movie_path_csv,soup, movie)

    similarPredictions_movieFilmList = []
    if currentUserId is not None :
        similarPredictions_movieFilmList = getMovieSimilarPredictions(currentUserId, movieTitle, movies_df, movieRatings_df, userRatingsMatrix, model, 6, 40)["movieTitle"].to_list()[1:]
        print("similarity : \n", similarPredictions_movieFilmList, "\n")
        soup = None
        for movie in (similarPredictions_movieFilmList):
            if not(os.path.exists(images_path + "scrap\\" + movie + ".jpg") or movie in failed_scraps):
                movieId = getMovieId(movie, movies_df)
                movieLink = getMovieImdbLink(movieId, links_df)
                print(movieLink)
                soup = request_soup(movieLink)
                response = scrap_image(soup, images_path=images_path, movieTitle=movie)
                if response == "ERROR_IMAGE": failed_scraps += [movieTitle]
                
            if movie not in df_movie_info['title'].values:
                movieId = getMovieId(movie, movies_df)
                movieLink = getMovieImdbLink(movieId, links_df)
                print(movieLink)
                soup = request_soup(movieLink)
                scrape_and_create_movie_csv(info_movie_path_csv,soup, movie)

            
    return render_template('movie_page_dynamic.html',
                            movieTitle=movieTitle,
                            listgenre=list_movie_genres,
                            listcast=list_movie_cast,
                            meanRating=mean_rating_movie,
                            images_path=images_path,
                            movie_Date = informations_movieDate,
                            movie_Time = informations_movieTime,
                            movie_Synopsis = informations_movieSynopsis,
                            movie_Director = informations_movieDirector,
                            currentUserId=currentUserId,
                            similarity_movieFilmList=similarity_movieFilmList,
                            similarPredictions_movieFilmList =similarPredictions_movieFilmList
                            )

@app.route('/myratings.html')
def my_ratings():
    MyRatingsPageCreation(currentUserId=currentUserId,
                    currentUserRatings=currentUserRatings,
                    file_path=templates_path + "myratings.html",
                    images_path=images_path, row_size=4)
    return render_template("myratings.html", currentUserId=currentUserId)

@app.route("/mypredictions.html")
def my_predictions():
    user_similarities_movies = getUserSimilarPredictions(userId=currentUserId,
                                                         movies_df=movies_df,
                                                         userRatings_df=userRatings_df,
                                                         movieRatings_df=movieRatings_df,
                                                         userRatingsMatrix=userRatingsMatrix,
                                                         model=model,
                                                         userAmount=10,
                                                         ratingsPerUser=10)
    print("user similarities : \n", user_similarities_movies["movieTitle"].iloc[:10], "\n")
    global failed_scraps
    for movie in user_similarities_movies["movieTitle"].values[:4]:
        if not(os.path.exists(images_path + "scrap\\" + movie + ".jpg") or movie in failed_scraps):
            movieId = getMovieId(movie, movies_df)
            movieLink = getMovieImdbLink(movieId, links_df)
            print(movieLink)
            soup = request_soup(movieLink)
            response = scrap_image(soup, images_path=images_path, movieTitle=movie)
            if response == "ERROR_IMAGE": failed_scraps += [movieTitle]
            
            if movie not in df_movie_info['title'].values:
                scrape_and_create_movie_csv(info_movie_path_csv,soup, movie)
    MyPredictionsPageCreation(currentUserId=currentUserId,
                            userPredictions=user_similarities_movies,
                            file_path=templates_path + "mypredictions.html",
                            images_path=images_path, row_size=4)
    return render_template("mypredictions.html", currentUserId=currentUserId)

@app.route("/_login", methods=["POST"])
def login():
    userId = request.form.get("userId")
    global currentUserId, currentUserRatings
    currentUserId = int(userId)
    print("connected as", currentUserId)
    currentUserRatings = userRatings_df[userRatings_df["userId"] == currentUserId].sort_values("rating", ascending=False)
    currentUserRatings["movieTitle"] = currentUserRatings["movieId"].apply(lambda id: getMovieTitle(movieId=id, movies_df=movies_df))
    return "Done!"

@app.route("/_disconnect", methods=["POST"])
def disconnect():
    global currentUserId
    currentUserId = None
    print("disconnecting..")
    return "Done!"

@app.context_processor
def handle_context():
    return dict(os=os)

if __name__ == '__main__':
    with app.app_context():
        if is_setup_tfidf_onStart:
            tfidf_matrix, tfidf_df = setup_tfidf(outBigData_path)
            print("tfidf setup!\n")
        if is_handle_movielens_onStart:
            print("setting up movielens dataset...")
            movies_df, links_df, tags_df, userRatings_df, movieRatings_df = read_movielens(path=movieLens_path, ratings_name="ratings_edit.csv")
            print("movielens dataset setup!")
        if is_getMovieMatrix_onStart:
            print("\nmaking MovieMatrix...")
            userRatingsMatrix = getUserRatingsMatrix(userRatings_df)
            print("movieMatrix done!\n")
        if is_setup_recommendation_model_onStart:
            print("\ncreating the prediction model...")
            model = createModel(userRatings_df, SVD)
            print("prediction model done!\n")
        if is_setup_movie_informations:
            df_movie_info = pd.read_csv(info_movie_path_csv)
            print("\nmovie informations read")
        if is_create_main_onStart:
            print("\ncreating main.html...")
            topMovies = getTopNMoviesByNbOfRatings(20, movies_df, movieRatings_df)["movieTitle"].to_list()
            MainPageCreation(movies=topMovies, file_path=templates_path + "main.html", images_path=images_path, row_size=4)
            print("main page created!\n")
        with open(images_path+"failed_images_scraps.txt", "r") as reader:
            failed_scraps = [movieTitle.strip() for movieTitle in reader.readlines()]

        print("\nlink : http://127.0.0.1:5000/")
    app.run(debug=False)
