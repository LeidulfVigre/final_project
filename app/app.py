from flask import Flask, redirect, url_for, render_template, request, session, make_response, jsonify
import db
import functions
import mysql.connector
import datetime

app = Flask(__name__)
app.secret_key = "monkey"

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        if session:
            return redirect(url_for("userPage", username=session["user_info"]["username"]))
        else:
            return render_template("startsite_login_register.html")

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
                redirect(url_for("userPage", username=session["user_info"]["username"]))
            )

            response.set_cookie("username", provided_username)
            return response

@app.route("/userPage/<username>", methods=["GET"])
def userPage(username):
    if request.method == "GET":
        owner = False
        
        if username == session["user_info"]["username"]:
            print("BLIR KJØRT!!!")
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
            reviewer_score = {"score":"Get to reviewing!","reviewer_status":"Nothing to see here yet.."}

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
        
        query = "SELECT Username FROM User WHERE Username = %s;"
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
                query = "INSERT INTO User VALUES (%s, %s, %s, %s, %s, %s, %s);"
                
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
                print("USERNAME HER: ", username)

                response = make_response(
                    redirect(url_for("userPage", username=session["user_info"]["username"]))
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

        user_id = session["user_info"]["user_id"]

        print(username, choose_review_rating, order_by_date, order_by_score, select_genre)

        username_session = session["user_info"]["username"]

        print(username_session)

        if not username or not choose_review_rating or not order_by_date or not order_by_score or not select_genre:
            return "Invalid parameters in URL", 403
        
        connection = db.get_connection()
        if not connection:
            return "Internal server error", 500
        
        query = functions.get_review_rating_both(choose_review_rating, order_by_date, order_by_score, select_genre)
        cursor = connection.cursor()

        if select_genre != "1":
            data = cursor.execute(query, (user_id, select_genre))
        else:
            data = cursor.execute(query, (user_id,))

        data = cursor.fetchall()
        print("DATA HER:", data)
        #print("TYPE OF DATA HER: ", type(data[0]))
        print("LEN OF DATA HER: ", len(data))
        cursor.close()
        connection.close()

        if len(data) > 0:
            if len(data[0]) == 5:
                many_attributes = False
            elif len(data[0]) == 10:
                many_attributes = True
            else:
                many_attributes = False
        else:
            many_attributes = False

        if username == username_session:
            owner = True
        print("BLIR KJØRT HER BLIR KJØRT HER")
        return render_template("partials/sorting_result_user_page.html", many_attributes=many_attributes, reviews_and_ratings=data, owner=owner)

@app.route("/write_review/<movie_id>", methods=["POST", "GET"])
def write_review(movie_id):
    if request.method == "GET":
        return render_template("write_review.html", movie_id=movie_id)
    elif request.method == "POST":
        review_title = request.form.get("review_title")
        review_text = request.form.get("review_text")
        review_rating = int(request.form.get("rating_of_movie"))
        user_id = session["user_info"]["user_id"]
        review_id = functions.generate_new_review_id()
        review_date = datetime.datetime.now()

        connection = db.get_connection()

        if not connection:
            return "Error connecting to database", 500
        cursor = connection.cursor()

        # We first have to make a query to rating to check if the user already have rated the movie
        query_rating_check = "SELECT Rating_ID, Rating_Score FROM Rating WHERE Movie_ID = %s AND User_ID = %s;"
        query_update_rating = ""
        cursor.execute(query_rating_check, (movie_id, user_id))
        rating_data = cursor.fetchone()
       # print("KOMMER SÅ LANGT")
        if rating_data:
            print("GÅR INN HER")
            rating_id = rating_data[0]
            query_update_rating = "UPDATE Rating SET Rating_Score = %s, Rating_Date = %s WHERE Rating_ID = %s;"

            try:
                cursor.execute(query_update_rating, (review_rating, review_date, rating_id))
                connection.commit()
            except Exception as e:
                connection.rollback()
                print("Something went wrong:", e)
                return "An error occured during update: ", 500
        else:
            rating_id = functions.generate_new_rating_id()
            query_update_rating = "INSERT INTO Rating VALUES (%s, %s, %s, %s, %s);"

            print("Jeg blir kjørt det går denne veien")
            print("Data i rating query: ", rating_id, review_rating, review_date, user_id, movie_id)

            try:
                cursor.execute(query_update_rating, (rating_id, review_rating, review_date, user_id, movie_id))
                connection.commit()
            except Exception as e:
                connection.rollback()
                print("BLIR KJØRT!")
                print("Something went wrong:", e)
                return "An error occured during update: ", 500
        
        query_review = "INSERT INTO Review VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"

        cursor.execute(query_review, (review_id, 0, 0, review_text, review_date, user_id, movie_id, rating_id, review_title)) 
        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("movie_site", movie_id=movie_id))
    
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
        cursor.execute(query, (actor_id,))
        actor_movies = cursor.fetchall()

        print("DEBUG actor_movies:", actor_movies)  # <-- add this

        cursor.close()
        connection.close()

        return render_template("actor_site.html", movies=actor_movies)
    
@app.route("/director_site/<director_id>", methods=["GET"])
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
        cursor.execute(query, (director_id,))
        director_movies = cursor.fetchall()

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
            print("JEG BLIR DESVERRE KJØRT!")
            return "Database connection failed", 500
        
        cursor = connection.cursor()

        query = "SELECT Movie_ID, Movie_Title, Release_Date FROM Movie WHERE Movie_Title LIKE %s ORDER BY Release_Date DESC;"
        cursor.execute(query, (f"%{movie_name}%",))
        search_results=cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template("partials/search_results.html", search_results=search_results)
    
@app.route("/movie_site/<movie_id>", methods=["GET"])
def movie_site(movie_id):
    if request.method == "GET":
        has_reviewed_movie = False
        has_written_review = False

        user_id = session["user_info"]["user_id"]
        
        movie_data = functions.get_movie_data_query(movie_id) 
        review_data = functions.get_reviews_from_movie_query(movie_id)        
        actor_data = functions.get_actors_in_movie_query(movie_id)
        director_data = functions.get_directors_in_movie_query(movie_id)

        print("Review data her: ", review_data)
       
        # Query information: Simple check to check if the user has rated the movie before
        rating_information = """
            SELECT User_ID, Rating_Score FROM Rating WHERE Movie_ID = %s AND User_ID = %s; 
        """
        # Query information: Simple check to check if the user has reviewed the movie before
        review_information = """
            SELECT User_ID FROM Review WHERE Movie_ID = %s AND User_ID = %s;
        """

        connection = db.get_connection()

        if not connection:
            return "Database connection failed", 500

        cursor = connection.cursor()
        cursor.execute(rating_information, (movie_id, user_id))
        rating_information_data = cursor.fetchone()

        cursor.execute(review_information, (movie_id, user_id))
        review_information_data = cursor.fetchone()

        cursor.close()
        connection.close()

        user_score = 0

        if rating_information_data:
            user_score = rating_information_data[1]
            has_reviewed_movie = True
        if review_information_data:
            has_written_review = True

        return render_template("movie_site.html", movie_data=movie_data, director_data=director_data, actor_data=actor_data, has_reviewed_movie=has_reviewed_movie, review_data=review_data, current_user_id=user_id, user_score=user_score, has_written_review=has_written_review) # IKKE FERDIG HER ENDA GJØR FERDIG!!
    

@app.route("/rate_movie", methods=["POST"])
def rate_movie():
    if request.method == "POST":
        data = request.get_json()
        value = data["selected_value"]
        movie_id = data["movie"]
        
        if not value:
            return "",400
        else:
            rating_id = functions.generate_new_rating_id()
            rating_score = int(value)
            current_date = datetime.datetime.now()
            user_id = session["user_info"]["user_id"]

            print("KOMMER FAKTISK SÅ LANGT")
            query = """
                INSERT INTO Rating VALUES (%s, %s, %s, %s, %s); 
            """

            try:
                connection = db.get_connection()
                cursor = connection.cursor()
                cursor.execute(query, (rating_id, rating_score, current_date, user_id, movie_id))
                connection.commit()
                cursor.close()
                connection.close()
                return "", 200
            except mysql.connector.Error as err:
                print("Error during insert: bruh ", err)
                return f"Server error: {err} ", 500

@app.route("/edit_review/<review_id>", methods=["GET","POST"])
def edit_review(review_id):
    if request.method == "GET":
        connection = db.get_connection()

        if not connection:
            return "Database connection failed",500

        query = "SELECT Review_Text, Review_Title FROM Review WHERE Review_ID = %s;"
        cursor = connection.cursor()

        cursor.execute(query, (review_id,))

        review_data = cursor.fetchone()
        cursor.close()
        connection.close()

        if not review_data:
            return "An error has occured. Invalid data: ", 403
        
        print("review data her: ", review_data)

        old_title = review_data[1]
        old_review = review_data[0]

        return render_template("edit_review.html", review_id=review_id,old_title=old_title,old_review=old_review)
    elif request.method == "POST":
        new_title = request.form.get("title")
        new_text = request.form.get("review_text")
        new_rating = int(request.form.get("rating"))
        current_date = datetime.datetime.now()

        if not new_title or not new_text or not new_rating:
            return "Invalid data sent", 403
        
        connection = db.get_connection()

        if not connection:
            return "Database connection failed", 500
        
        cursor = connection.cursor()

        # Query information. Gets the relevant rating id so we can also update the rating
        query = "SELECT Rating_ID FROM Review WHERE Review_ID = %s;"
        cursor.execute(query, (review_id,))
        data = cursor.fetchone()
        rating_id = data[0]

        update_rating_query = "UPDATE Rating SET Rating_Score = %s, Rating_Date = %s WHERE Rating_ID = %s;"
        update_review_query = "UPDATE Review SET Review_Text = %s, Review_Date = %s, Review_Title = %s WHERE Review_ID = %s;"
        
        try:
            cursor.execute(update_rating_query, (new_rating, current_date, rating_id))
            cursor.execute(update_review_query, (new_text, current_date, new_title, review_id))
            connection.commit()
        except Exception as e:
            connection.rollback()
            print("Something went wrong:", e)
            return "An error occured during update: ", 500
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("userPage", username=session["user_info"]["username"]))

@app.route("/delete_review", methods=["POST"])
def delete_review():
    if request.method == "POST":
        data = request.get_json()
        review_id = data["selected_review"]
        connection = db.get_connection()

        if not connection:
            return "Connection to database failed", 500
        cursor = connection.cursor()

        # Query information. Gets the relevant rating id so we can also delete the rating
        query = "SELECT Rating_ID FROM Review WHERE Review_ID = %s;"
        cursor.execute(query, (review_id,))
        data = cursor.fetchone()
        rating_id = data[0]

        delete_rating_query = "DELETE FROM Rating WHERE Rating_ID = %s;"
        delete_review_query = "DELETE FROM Review WHERE Review_ID = %s;"

        try:
            cursor.execute(delete_review_query, (review_id,))
            cursor.execute(delete_rating_query, (rating_id,))
            connection.commit()
        except Exception as e:
            connection.rollback()
            print("Error during deletion")
            return "An error occured during deletion", 500
        finally:
            cursor.close()
            connection.close()
        
        return jsonify({"success": True, "username": session["user_info"]["username"]}) 

@app.route("/edit_user/<user_name>", methods=["GET", "POST"])
def edit_user(user_name):
    if request.method == "GET":
        connection = db.get_connection()

        if not connection:
            return "Connection to database failed", 500
        user_data_query = "SELECT First_Name, Last_Name FROM User WHERE Username = %s;"

        cursor = connection.cursor()
        cursor.execute(user_data_query, (user_name,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user_data:
            return "Failed to fetch data from user",500

        firstname = user_data[0]
        lastname = user_data[1]
        
        return render_template("edit_user.html", old_username=user_name, old_firstname=firstname, old_lastname=lastname, username_taken=False)    
    elif request.method == "POST":
        new_username = request.form.get("username")
        new_firstname = request.form.get("firstname")
        new_lastname = request.form.get("lastname")
        new_password = request.form.get("password")
        user_id = session["user_info"]["user_id"]
        new_hashed_password = functions.hash_password(new_password)

        connection = db.get_connection()

        if not connection:
            return "Connection to database failed", 500
        
        cursor = connection.cursor()

        query_username = "SELECT * FROM User WHERE Username = %s;"
        

        cursor.execute(query_username, (new_username,))
        user_data = cursor.fetchone()

        if user_data:
            if user_data[0] != session["user_info"]["user_id"]:
                user_data_query = "SELECT First_Name, Last_Name FROM User WHERE Username = %s;"

                cursor = connection.cursor()
                cursor.execute(user_data_query, (user_name,))
                user_data = cursor.fetchone()
                cursor.close()
                connection.close()

                firstname = user_data[0]
                lastname = user_data[1]

                return render_template("edit_user.html",old_username=session["user_info"]["username"], old_firstname=firstname, old_lastname=lastname, username_taken=True)
        
        update_user_info_query = "UPDATE User SET Username = %s, First_Name = %s, Last_Name = %s, Password_Hash = %s WHERE User_ID = %s;"

        try:
            cursor.execute(update_user_info_query, (new_username, new_firstname, new_lastname, new_hashed_password, user_id))
            connection.commit()
        except Exception as e:
            connection.rollback()
            print("Something went wrong:", e)
            print("Jeg blir kjørt. En error skjedde")
            return "An error occured during update: ", 500
        finally:
            cursor.close()
            connection.close()

        session["user_info"]["username"] = new_username
        session["user_info"]["password"] = new_password
        session.modified = True
        
        return redirect(url_for("userPage", username=session["user_info"]["username"]))
    
@app.route("/delete_user", methods=["POST"])
def delete_user():
    # Må først slette alle reviews til brukeren, så slettes ratingsene, så må brukeren slettes.
    if request.method == "POST":
        user_id = session["user_info"]["user_id"]
        connection = db.get_connection()
        
        if not connection:
            return "Connection to database failed",500
        
        cursor = connection.cursor()
    
        delete_reviews_query = "DELETE FROM Review WHERE User_ID = %s;"
        delete_ratings_query = "DELETE FROM Rating WHERE User_ID = %s;"
        delete_user_query = "DELETE FROM User WHERE User_ID = %s;"

        try:
            cursor.execute(delete_reviews_query, (user_id,))
            cursor.execute(delete_ratings_query, (user_id,))
            cursor.execute(delete_user_query, (user_id,))
            connection.commit()
        except Exception as e:
            connection.rollback()
            print("Error during deletion", e)
            return "An error occured during deletion", 500
        finally:
            cursor.close()
            connection.close()
        
        session.clear()
        response = redirect(url_for("login"))
        
        return jsonify({"success":True})


@app.route("/show_all_movies", methods=["GET"])
def show_all_movies():
    if request.method == "GET":
        connection = db.get_connection()
        if not connection:
            return "Connection to database failed",500
        # Query information:
        # joining the movie table with a subquery which finds the average rating score for each movie.
        # We have to make it a left join so that the movies with no reviews yet can also be listed
        query = """
            SELECT m.Movie_ID, m.Movie_Title, m.Release_Date, average_ratings_movies.average_ratings
            FROM Movie m 
            LEFT JOIN (
                SELECT Movie_ID, AVG(Rating_Score) as average_ratings
                FROM Rating
                GROUP BY  Movie_ID
            ) AS average_ratings_movies
            ON m.Movie_ID = average_ratings_movies.Movie_ID
            ORDER BY m.Release_Date ASC; 
        """

        cursor = connection.cursor()

        cursor.execute(query)
        all_movies = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template("show_all_movies.html", movies=all_movies)

@app.route("/log_out", methods=["GET"])
def log_out():
    if request.method == "GET":
        session.clear()
        return redirect(url_for("index"))

"""
Lag en all movies side som lister opp alle filmene som er registrert i databasen i alfabetisk rekkefølge.
Gjør dette siden vi må ha med et group by 
"""

if __name__ == "__main__":
    app.run(debug=True)