from flask import Flask, redirect, url_for, render_template, request, session, make_response
import db
import functions
import mysql.connector

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
        query = "SELECT User_ID, Username, User_Type, Password_Hash FROM User WHERE Username = %s"

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
            session["user_info"] = {
                "user_id":user_data[0], 
                "username":user_data[1],
                "user_type":user_data[2],
                "password":user_data[3]
            }
            
            response = make_response(
                redirect(url_for("userPage"))
            )

            response.set_cookie("username", provided_username)
            return response

@app.route("/userPage/<username>", methods=["GET"])
def userPage(username):
    if request.method == "GET":
        owner = False
        
        if username == session["user_info"]["username"]:
            owner = True
            user_id = session["user_info"]["user_id"]
        else:
            user_id = None

        connection = db.get_connection()
        if connection == None:
            return "Error connecting to database: ", 500

        query_reviewer_score = "SELECT User_ID, Reviewer_Score FROM User WHERE Username = %s" # Gets separatively because of redundancy in the join operation
        cursor = connection.cursor()
        cursor.execute(query_reviewer_score, (username,))
        reviewer_score_fetch = cursor.fetchone()
        cursor.close()

        user_id = reviewer_score_fetch[0]
        

        if reviewer_score_fetch[1] > 0:
            if reviewer_score_fetch[1] > 3:
                reviewer_score = {"score":reviewer_score_fetch[0], "reviewer_status":"Reliable"}
            else:
                reviewer_score = {"score":reviewer_score_fetch[0],"reviewer_status":"Unreliable"}
        else:
            reviewer_score = {"score":reviewer_score_fetch[0],"reviewer_status":"Nothing to see here yet.."}

        # Query with a join between three tables: Rating, Review and Movie. Getting all Ratings and reviews a user has made.
        # This query uses a left join to get all ratings, even those without a review attached to it, along with the reviews.
        # After the left join, the table from the left join, joins with the movie table to get the title of the movie for the rating/review.
        query = """
            SELECT m.Movie_Title,   0
                   m.Movie_ID,      1
                   rv.Review_Title, 2
                   rv.Likes,        3
                   rv.Dislikes,     4
                   rv.Review_Text,  5
                   r.Rating_Score,  6
                   r.Rating_Date    7
            FROM Rating r 
            LEFT JOIN Review rv ON r.Rating_ID = rv.Rating_ID
            INNER JOIN Movie m ON r.Movie_ID = m.Movie_ID
            WHERE Rating.User_ID = %s
            ORDER BY r.Rating_Date DESC;
        """
        cursor = connection.cursor()
        cursor.execute(query, (user_id,))

        rating_and_review_data = cursor.fetchall()
        cursor.close()
        connection.close()

        

        return render_template("user_page.html", owner=owner, username=username, reviews_and_ratings=rating_and_review_data, reviewer_score=reviewer_score)

@app.route("/user_registration", methods=["POST", "GET"])
def user_registration():
    if request.method == "GET":
        return render_template("user_registration.html", username_already_exists=False)
    elif request.method == "POST":
        suggested_username = request.form.get("registered_username")
        suggested_password = request.form.get("registered_password")
        
        connection = db.get_connection()

        if not connection:
            return "Error connecting to database", 500
        
        query = "SELECT Username FROM User WHERE Username = %s"
        cursor = connection.cursor()
        cursor.execute(query, (suggested_username,))

        fetched_data = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not fetched_data:
            user_id = functions.generate_new_user_id()
            username = suggested_username
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            user_type = "N"
            reviewer_score = -1
            password_hash = functions.generate_password_hash(suggested_password)

            try:
                query = "INSERT INTO User VALUES (%s, %s, %s, %s, %s, %s, %s)"
                
                cursor = connection.cursor()
                cursor.execute(query, (user_id,username,first_name,last_name,user_type,reviewer_score,password_hash))
                connection.commit()
                cursor.close()
                connection.close()

                session["user_info"] = {
                    "user_id":user_id, 
                    "username":username,
                    "user_type":"N",
                    "password":password_hash
                }

                response = make_response(
                    redirect(url_for("userPage"))
                )

                response.set_cookie("username", suggested_password)
                return response

            except mysql.connector.Error as err:
                print("Error during insert: ", err)
                return f"Server error: {err} ", 500
        else:
            return render_template("user_registration.html", username_already_exists=True)

@app.route("/handle_review_rating_both", methods=["GET"])
def handle_review_rating_both():
    if request.method == "GET":
        username = request.args.get("username")
        choice = request.args.get("choice")

        if not username or not choice:
            return "Invalid parameters in URL", 403
        
        connection = db.get_connection()
        if not connection:
            return "Internal server error", 500
        
        if choice == "1":
            query = """
        
"""

        query = """

        """
        cursor = connection.cursor()


@app.route("/write_review", methods=["POST", "GET"])
def write_review():
    if request.method == "GET":
        return render_template("write_review.html", review_text="")
    elif request.method == "POST":
        review_text = request.form.get("review_text")
        user_id = session.get("id")
        movie_id = 1 # Just a placeholder for now
        rating_score = 4 # Could be a form field later
        review_date = datetime.now()

        connection = db.get_connection()

        if not connection:
            return "Error connecting to database", 500

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Rating (Rating_ID, Rating_Score, Rating_Date, User_ID, Movie_ID) VALUES (NULL, %s, %s, %s, %s)",
            (rating_score, review_date, user_id, movie_id)
        )
        connection.commit()
        rating_id = cursor.lastrowid

        # Insert review using the rating_id we just got
        cursor.execute(
            "INSERT INTO Review (Review_ID, Likes, Dislikes, Review_Text, Review_Date, User_ID, Movie_ID, Rating_ID) VALUES (NULL, 0, 0, %s, %s, %s, %s, %s)",
            (review_text, review_date, user_id, movie_id, rating_id)
        )
        connection.commit()

        cursor.close()
        connection.close()

        return "Review submitted!"

if __name__ == "__main__":
    app.run(debug=True)