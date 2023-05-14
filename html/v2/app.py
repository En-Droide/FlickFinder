from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    from result import a  # Import the list from the Result.py file
    result = str(a)  # Convert the list to a string
    return render_template("result.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
