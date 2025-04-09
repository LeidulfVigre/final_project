from flask import Flask, redirect, url_for, render_template, request, session, make_response
import db
import functions

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
        username = request.cookies.get("username")
        password = session.get("password")

        if not username and not password:
            username = "username"
            password = "password"

        return render_template("login_page.html", username=username, password=password) 
    elif request.method == "POST":
        connection = db.get_connection()

        if connection == None:
            return "Error connecting to the database", 500

        provided_password = request.form.get("password")
        provided_username = request.form.get("username")
        query = "SELECT User_ID, Username, User_Type, User_Type, Password_Hash FROM User WHERE Username = %s"

        cursor = connection.cursor()
        cursor.execute(query, (provided_username,))
        user_data = cursor.fetchone()
        cursor.close() 
        connection.close()

        if not user_data:
            return render_template("login_page.html", failed_login=True)

        if not functions.check_login(provided_password, user_data[4]):
            return render_template("login_page.html", failed_login=True)
        else:
            session["password"] = user_data[4]
            session["id"] = user_data[0]
            response = make_response(
                redirect(url_for("userPage"))
            )

            response.set_cookie("username", provided_username)
            return response

@app.route("/userPage")
def userPage():

    return "for å unngå error"

@app.route("/user_registration", methods=["POST", "GET"])
def user_registration():
    if request.method == "GET":
        return render_template("user_registration.html", username_already_exists=False)
    elif request.method == "POST":
        suggested_username = request.form.get("registered_username")
        
        connection = db.get_connection()

        if not connection:
            return "Error connecting to database", 500
        
        query = "SELECT Username FROM User WHERE Username = %s"
        cursor = connection.cursor()
        cursor.execute(query, (suggested_username,))

        fetched_data = cursor.fetchone()
        
        if fetched_data[0]:
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            password = request.form.get("passw")
        else:
            return render_template("user_registration.html", username_already_exists=True)

#@app.route("/")

if __name__ == "__main__":
    app.run(debug=True)