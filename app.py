from flask import Flask, render_template, request, abort
import logging
import os
import sys

project_path = "C:\\Users\\lotod\\OneDrive\\Bureau\\GIT\\FlickFinder\\"
# project_path = "C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\"

is_setup_tfidf_onStart = True
is_handle_movielens_onStart = True
is_getMovieMatrix_onStart = False
is_create_main_onStart = True

instance_path = project_path
templates_path = instance_path + "templates\\"
images_path = instance_path + "static\\Images\\"
python_path = instance_path + "Python_files\\"
sys.path.insert(1, python_path)
movieLens_path = python_path + "csv_files\\ml-latest\\"
rating_path = movieLens_path + "ratings.csv"
outBigData_path = python_path + "csv_files\\out_big_data.csv"


from handle_movielens import read_movielens, getUserRatingsMatrix, getMovieId, getMovieTitle, getMovieImdbLink, getMovieRatingsByIndex, isMovieInDataset, getTopNMoviesByNbOfRatings
from tfidf import start_tfidf, setup_tfidf, get_movie_genres_cast
from create_similar_movies import SimilarPageCreation
from create_main import MainPageCreation
from scrap import request_soup, scrap_image, scrape_and_create_movie_json


app = Flask(__name__, instance_path=instance_path)
app.config["TEMPLATES_AUTO_RELOAD"] = True
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/main.html")
def main():
    return render_template("main.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/account.html")
def account():
    return render_template("account.html")

@app.route("/exemple_movie_page.html")
def moviePage():
    return render_template("exemple_movie_page.html")

@app.route("/_tfidf", methods=["POST"])
def createPage():
    movieTitle = request.form.get("searchText")
    movieFilmList = start_tfidf(tfidf_df, tfidf_matrix, movieTitle, size=19)
    print(movieFilmList)
    global failed_scraps
    for movie in movieFilmList[:4]:
        if not(os.path.exists(images_path + "scrap\\" + movie + ".jpg") or movie in failed_scraps):
            movieId = getMovieId(movie, movies_df)
            movieLink = getMovieImdbLink(movieId, links_df)
            print(movieLink)
            soup = request_soup(movieLink)

            a= scrape_and_create_movie_json(soup, movie)
            print(a)
            response = scrap_image(soup, images_path=images_path, movieTitle=movie)
            if response == "ERROR_IMAGE": failed_scraps += [movieTitle]
    SimilarPageCreation(movies=movieFilmList, file_path=templates_path + "similar_movies.html", images_path=images_path, row_size=4)
    return "Done!"

@app.route('/similar_movies.html')
def similar_movies():
    return render_template('similar_movies.html')


@app.route('/_movie/<movieTitle>')
def movie_page2(movieTitle):
    print(movieTitle)
    # movieTitle="Toy Story (1995)"
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
    return render_template('movie_page_dynamic.html',
                           movieTitle=movieTitle,
                           listgenre=list_movie_genres,
                           listcast=list_movie_cast,
                           meanRating=mean_rating_movie,
                           images_path=images_path)

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
            movies_df, links_df, tags_df, userRatings_df, movieRatings_df = read_movielens(path=movieLens_path, size=1000000)
            print("movielens dataset setup!")
        if is_getMovieMatrix_onStart:
            print("making MovieMatrix...")
            userRatingsMatrix = getUserRatingsMatrix(userRatings_df)
            print("movieMatrix done!\n")
        if is_create_main_onStart:
            print("\ncreating main.html...")
            topMovies = getTopNMoviesByNbOfRatings(20, movies_df, movieRatings_df)["movieTitle"].to_list()
            MainPageCreation(movies=topMovies, file_path=templates_path + "main.html", images_path=images_path, row_size=4)
            print("main page created!\n")

        with open(images_path+"failed_images_scraps.txt", "r") as reader:
            failed_scraps = [movieTitle.strip() for movieTitle in reader.readlines()]

            print("")
        print("link : http://127.0.0.1:5000/")
    app.run(debug=False)
