from flask import Flask, render_template, request
import os
import sys

# sys.path.insert(1, 'C:\\Users\\lotod\\OneDrive\\Bureau\\GIT\\FlickFinder\\html\\v2\\Python_files')
# file_name = ('C:\\Users\\lotod\\OneDrive\\Bureau\\GIT\\FlickFinder\\python\\out_big_data.csv')
# my_path = "C:\\Users\\lotod\\OneDrive\\Bureau\\GIT\\FlickFinder\\html\\v2"

sys.path.insert(1, 'C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\html\\v2\\Python_files')
file_name = "C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\python\\out_big_data.csv"
my_path = "C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\html\\v2"

app = Flask(__name__, instance_path=my_path)

from tfidf import start_tfidf
from html_creation import PageCreation

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

@app.route("/_postExemple", methods=["POST"])
def test():
    message = request.form.get("myMessage")
    movieFilmList = start_tfidf(file_name,message)
    PageCreation(movieFilmList,"C:\\Users\\MatyG\\Documents\\Annee_2022_2023\\Projet_films\\FlickFinder\\html\\v2\\templates\\output.html")
    return movieFilmList

@app.route('/output.html')
def output():
    return render_template('output.html')


if __name__ == '__main__':
    app.run(debug=True)
