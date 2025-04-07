from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":     
        return render_template("startsite_login_register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        print("test")
        return "hei"
    elif request.method == "POST":
        return "hei 2"