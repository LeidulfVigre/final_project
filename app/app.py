from flask import Flask, redirect, url_for, render_template, request, session, make_response
import db
import functions
import mysql.connector
import datetime

app = Flask(__name__)
app.secret_key = "monkey"

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

        if not functions.check_login(provided_password, user_data[3]):
            print(user_data[3])
            return render_template("login_page.html", failed_login=True)
        else:
            session["user_info"] = {
                "user_id":user_data[0], 
                "username":user_data[1],
                "user_type":user_data[2],
                "password":user_data[3]
            }
            
            response = make_response(
                redirect(url_for("userPage", usermame=session["user_info"]["username"]))
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
            SELECT m.Movie_Title,   
                   m.Movie_ID,      
                   rv.Review_ID,
                   rv.Review_Title, 
                   rv.Likes,        
                   rv.Dislikes,     
                   rv.Review_Text,  
                   r.Rating_ID,
                   r.Rating_Score,  
                   r.Rating_Date
            FROM Rating r 
            LEFT JOIN Review rv ON r.Rating_ID = rv.Rating_ID
            INNER JOIN Movie m ON r.Movie_ID = m.Movie_ID
            WHERE r.User_ID = %s
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
        print(connection)
        
        if connection and connection.is_connected():
            print("det er faktisk en kobling her!!!")

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
                connection = db.get_connection()
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
                print("Error during insert: bruh ", err)
                return f"Server error: {err} ", 500
        else:
            return render_template("user_registration.html", username_already_exists=True)

@app.route("/handle_sorting", methods=["GET"])
def handle_review_rating_both():
    if request.method == "GET":
        username = request.args.get("username")
        choose_review_rating = request.args.get("choose_review_rating")
        order_by_date = request.args.get("order_by_date")
        order_by_score = request.args.get("order_by_score")
        select_genre = request.args.get("select_genre")

        username_session = session["user_info"]["username"]

        if not username or not choose_review_rating or not order_by_date or not order_by_score or not select_genre:
            return "Invalid parameters in URL", 403
        
        connection = db.get_connection()
        if not connection:
            return "Internal server error", 500
        
        query = functions.get_review_rating_both(choose_review_rating, order_by_date, order_by_score, select_genre)
        cursor = connection.cursor()

        if select_genre != "1":
            data = cursor.execute(query, (username, select_genre))
        else:
            data = cursor.execute(query, (username,))

        data = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(data) > 0:
            if len(data[0] == 4):
                many_attributes = False
            elif len(data[0] == 8):
                many_attributes = True
        else:
            many_attributes = False

        if username == username_session:
            owner = True

        return render_template("partials/sorting_result_user_page.html", many_attributes=many_attributes, reviews_and_ratings=data, owner=owner)

@app.route("/movie_site/<movie_id>")
def movie_site(movie_id): 
    if request.method == "GET":
        return "for å unngå error"

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
    
@app.route("/actor_site/<int:actor_id>", methods=["GET"])
def actor_site(actor_id):
    connection = db.get_connection()
    if not connection:
        return "Database connection failed", 500

    if request.method == "GET":

        query = """
            SELECT  m.Movie_Title,
                    a.Actor_First_Name,
                    a.Actor_Last_Name,
                    a.Date_Of_Birth,
                    a.Height,
                    ma.Character_Name,
                    m.Movie_ID
            FROM Movie m
            INNER JOIN Actor_And_Movie ma
            ON m.Movie_ID = ma.Movie_ID
            INNER JOIN Actor a
            ON a.Actor_ID = ma.Actor_ID
            WHERE a.Actor_ID = %s
        """

        cursor = connection.cursor()
        #cursor.execute(query, (actor_id,))
        #actor_movies = cursor.fetchall()

        actor_movies = [
            ("Snow White", "Gal", "Gadot", "1985-30-04", 178, "Witch", 1),
            ("Justice League", "Gal", "Gadot", "1985-30-04", 178, "Wonder Woman", 2)
        ]

        print("DEBUG actor_movies:", actor_movies)  # <-- add this

        cursor.close()
        connection.close()

        return render_template("actor_site.html", movies=actor_movies)
    
@app.route("/director_site/<int:director_id>", methods=["GET"])
def director_site(director_id):
    connection = db.get_connection()
    if not connection:
        return "Database connection failed", 500

    if request.method == "GET":

        query = """
            SELECT  m.Movie_Title,
                    d.Director_First_Name,
                    d.Director_Last_Name,
                    d.Date_Of_Birth,
                    d.Height,
                    m.Movie_ID
            FROM Movie m
            INNER JOIN Director_And_Movie md
            ON m.Movie_ID = md.Movie_ID
            INNER JOIN Director d
            ON d.Director_ID = md.Director_ID
            WHERE d.Director_ID = %s
        """

        cursor = connection.cursor()
        #cursor.execute(query, (director_id,))
        #director_movies = cursor.fetchall()

        director_movies = [
            ("Ready Player One", "Steven", "Spielberg", "1946-18-12", 172, 1),
            ("Jaws", "Steven", "Spielberg", "1946-18-12", 172, 2)
        ]

        print("DEBUG director_movies:", director_movies)  # <-- add this

        cursor.close()
        connection.close()

        return render_template("director_site.html", movies=director_movies)

@app.route("/search", methods=["GET"])
def search():
    if request.method == "GET":
        movie_name = request.args.get("movie_name")

        connection = db.get_connection()
        if not connection:
            return "Database connection failed", 500
        
        cursor = connection.cursor()

        query = "SELECT Movie_ID, Movie_Title, Release_Date FROM Movie WHERE Movie_Title = %s ORDER BY Release_Date DESC"
        cursor.execute(query, (movie_name,))
        search_results=cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template("search_results.html", search_results=search_results)
@app.route("/movie_site/<movie_id>", methods=["GET"])
def movie_site(movie_id):
    if request.method == "GET":
        has_reviewed_movie = False
        user_id = session["user_info"]["user_id"]
        
        movie_data = functions.get_movie_data_query(movie_id) 
        review_data = functions.get_reviews_from_movie_query(movie_id)        
        actor_data = functions.get_actors_in_movie_query(movie_id)
        director = functions.get_directors_in_movie_query(movie_id)

        #beskjed til meg selv:
        # Husk at en enkel måte å få med seg group by på er å lage en film fremside som lister opp alle filmene. 
        # her kan man altså bruke group by movie id og finne average av filmene!!!
       
        # Query information: Simple check to check if the user has reviewed the movie before
        rating_information = """
            SELECT User_ID FROM Rating WHERE Movie_ID = %s AND User_ID = %s; 
        """

        connection = db.get_connection()
        cursor = connection.cursor()
        cursor.execute(rating_information, (movie_data, user_id))
        rating_information_data = cursor.fetchone()

        if rating_information_data:
            has_reviewed_movie = True

        return render_template("movie_site-html", movie_data=movie_data, ) # IKKE FERDIG HER ENDA GJØR FERDIG!!
    

@app.route("/rate_movie", methods=["POST"])
def rate_movie():
    if request.method == "POST":
        data = request.get_json()
        value = data["selected_value"]
    

# OBS LAG ET ENDEPUNKT SOM HETER handle_liking_review som tar seg av det å like et review til en bruker



"""
Lag en all movies side som lister opp alle filmene som er registrert i databasen i alfabetisk rekkefølge.
Gjør dette siden vi må ha med et group by 
"""

if __name__ == "__main__":
    app.run(debug=True)