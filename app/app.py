from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":     
        return render_template("startsite_login_register.html")

@app.route("/movie_site", methods=["GET"])
def movie_site():
    if request.method == "GET":
        return render_template("movie_site.html", movie_name="Revenge of the Sith", score="5", duration="2 timer", genre="Science Fiction", age_limit="12", release_date="2001", synopsis="Bra film", country_of_origin="USA", movie_language="English")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        print("test")
        return "hei"
    elif request.method == "POST":
        return "hei 2"