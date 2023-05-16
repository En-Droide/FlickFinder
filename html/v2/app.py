from flask import Flask, render_template, request
import os

my_path = "C:\\Users\\lotod\\OneDrive\\Bureau\\GIT\\FlickFinder\\html\\v2"
app = Flask(__name__, instance_path=my_path)

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
    return message

if __name__ == '__main__':
    app.run(debug=True)