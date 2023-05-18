from flask import Flask, render_template, request, g
import os
import sys

# project_path = "C:\\Users\\lotod\\OneDrive\\Bureau\\GIT\\FlickFinder\\"
project_path = "C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\"

is_setup_tfidf_onStart = True
is_handle_movielens_onStart = True
is_getMovieMatrix_onStart = False

instance_path = project_path + "html\\v2\\"
sys.path.insert(1, instance_path + "Python_files")
templates_path = instance_path + "templates\\"
images_path = instance_path + "static\\Images\\"
rating_path = project_path + "\\python\\csv_files\\ml-latest\\ratings.csv"
outBigData_path = project_path + "python\\out_big_data.csv"


from handle_movielens import read_movielens, getMovieMatrix, getMovieId, getMovieImdbLink
from tfidf import start_tfidf, setup_tfidf, movie_genres_cast
from similar_movies_creation import PageCreation
from scrap_image import scrap
from movie_page_creation import open_movie_page

app = Flask(__name__, instance_path=instance_path)
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

@app.route("/movie_page.html")
def moviePage():
    return render_template("movie_page.html")

@app.route("/_tfidf", methods=["POST"])
def createPage():
    movieTitle = request.form.get("searchText")
    movieFilmList = start_tfidf(tfidf_df, tfidf_matrix, movieTitle, size=20)
    PageCreation(movies=movieFilmList, file_path=templates_path + "similar_movies.html", images_path=images_path, row_size=4)
    print(movieFilmList)
    for movie in movieFilmList[:3]:
        if not(os.path.exists(images_path + "scrap\\" + movie + ".jpg")):
            movieId = getMovieId(movie, movies_df)
            movieLink = getMovieImdbLink(movieId, links_df)
            print(movieLink)
            try:
                scrap(movieLink, path=images_path+"scrap\\"+movie.replace("'", "&quot;"))
            except:
                print("error scraping", movie)
    return "Done!"

@app.route('/similar_movies.html')
def similar_movies():
    return render_template('similar_movies.html')

@app.route('/_movie/<movieTitle>')
def movie_page(movieTitle):
    print(movieTitle)
    movieTitle="Toy Story (1995)"
    list_movie_genres, list_movie_cast  = movie_genres_cast(tfidf_df, movieTitle)
    open_movie_page(file_path=templates_path+"charac_movie.html", movieTitle=movieTitle, listgenre=list_movie_genres, listcast=list_movie_cast)
    return render_template('charac_movie.html')

if __name__ == '__main__':
    with app.app_context():
        if is_setup_tfidf_onStart:
            tfidf_matrix, tfidf_df = setup_tfidf(outBigData_path)
            print("tfidf setup !")
        if is_handle_movielens_onStart:
            print("\nsetting up movielens dataset...")
            movies_df, links_df, tags_df, userRatings_df, movieRatings_df = read_movielens(path=project_path+"python\\csv_files\\ml-latest\\", size=1000000)
            print("movielens dataset setup!")
        if is_getMovieMatrix_onStart:
            print("making MovieMatrix...")
            movieMatrix = getMovieMatrix(userRatings_df)
            print("movieMatrix done!\n")
    app.run(debug=True)
