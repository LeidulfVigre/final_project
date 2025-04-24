"""
File with helper functions
"""
from werkzeug.security import generate_password_hash, check_password_hash
import random
import mysql.connector
import db

# Function for checking a valid login.
def check_login(provided_password, stored_password):
    
    if check_password_hash(stored_password, provided_password):
        return True
    else:
        return False
  
# Function for hashing a password for a new user 
def hash_password(provided_password):
    return generate_password_hash(provided_password)

# Function for generating a new user ID:
def generate_new_user_id():
    valid_id = False
    new_id = -1

    while not valid_id:
        new_id = random.randint(1000000,9999999)

        query = "SELECT User_ID FROM User WHERE User_ID = %s;"
        connection = db.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (new_id,))
        user_data = cursor.fetchone()
        if not user_data:
            valid_id = True
            cursor.close()
            connection.close()
    
    return new_id

# Function for generating a new rating ID:
def generate_new_rating_id():
    valid_id = False
    new_id = -1

    while not valid_id:
        new_id = random.randint(1000000,9999999)

        query = "SELECT Rating_ID FROM Rating WHERE Rating_ID = %s;"
        connection = db.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (new_id,))
        rating_data = cursor.fetchone()

        if not rating_data:
            valid_id = True
            cursor.close()
            connection.close()
    
    return new_id

# Function for generating a new review ID:
def generate_new_review_id():
    valid_id = False
    new_id = -1

    while not valid_id:
        new_id = random.randint(1000000, 9999999)

        query = "SELECT Review_ID FROM Review WHERE Review_ID = %s;"
        connection = db.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (new_id,))
        review_data = cursor.fetchone()

        if not review_data:
            valid_id = True
            cursor.close()
            connection.close()
    return new_id
    
# Function for getting relevant query from 
def get_review_rating_both(choose_review_rating, order_by_date, order_by_score, select_genre):

    # fjern urelevante kommentarer etterpå!!
    # bygger basically queriet ut i fra hvilke valg som er tatt
    # dette betyr også at jeg bare trenger et partial template for å oppdatere review og rating feltet!!
    # HENT UT REVIEW ID OG RATING ID. LEGG TIL DISSE I URL-en TIL EDIT KNAPPENE I USER_PAGE TEMPLATE OG PARTIAL TEMPLATE!!!!
    query = ""
    
    if choose_review_rating == "1":
        query += """
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
            FROM Review rv 
            INNER JOIN Rating r ON rv.Rating_ID = r.Rating_ID
            INNER JOIN Movie m ON rv.Movie_ID = m.Movie_ID
            WHERE rv.User_ID = %s
        """
    elif choose_review_rating == "2":
        query += """
            SELECT m.Movie_Title, 
                   m.Movie_ID,      
                   r.Rating_ID,     
                   r.Rating_Score,  
                   r.Rating_Date
            FROM Rating r
            INNER JOIN Movie m ON r.Movie_ID = m.Movie_ID
            WHERE r.User_ID = %s
        """
    elif choose_review_rating == "3":
        query += """
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
        """
    else:
        return None  # Or raise an error if the input is invalid

    # Add genre filter if selected
    if select_genre != "1":
        query += " AND m.Genre = %s"

    # Add sorting
    sort_parts = []

    if order_by_date == "1":
        sort_parts.append("r.Rating_Date ASC")
    elif order_by_date == "2":
        sort_parts.append("r.Rating_Date DESC")

    if order_by_score == "1":
        sort_parts.append("r.Rating_Score DESC")
    elif order_by_score == "2":
        sort_parts.append("r.Rating_Score ASC")

    if sort_parts:
        query += " ORDER BY " + ", ".join(sort_parts)

    query += ";"
    
    return query

# Function for getting the relevant query for a specific movie
def get_reviews_from_movie_query(movie_id):
    # Query information:
    # Query where all reviews and related ratings are retrieved. 
    # Bruk denne til å hente informasjon om alle reviews her
    review_query = """
        SELECT 
            rv.Review_ID,
            rv.Likes,
            rv.Dislikes,
            rv.Review_Text,
            rv.Review_Date,
            rv.Review_Title,
            r.Rating_Score,
            u.User_ID,
            u.Username
        FROM Review rv
        JOIN Rating r
        ON rv.Rating_ID = r.Rating_ID
        JOIN User u
        ON rv.User_ID = u.User_ID
        WHERE rv.Movie_ID = %s;
    """        
    connection = db.get_connection()
    if not connection:
        return False
    else:
        cursor = connection.cursor()
        cursor.execute(review_query, (movie_id,))
        review_data = cursor.fetchall()
        cursor.close()
        connection.close()

        return review_data

# Function for getting information about the movie
def get_movie_data_query(movie_id):
    # Query information:
    # Analytical query, that is, an aggregation query getting the average score for a specific movie
    # When doing query between a one to many relationship this is fine, but combining this with a many to many
    # relation can be messy. Here I am using a subquery to aggregate the ragting and joining it with movie to get all information needed. 
    # Bruk denne til å hente informasjon om filmen her:)
    aggregation_query = """
        SELECT m.*,
                average_ratings.Average_Score
        FROM Movie m
        LEFT JOIN (
            SELECT Movie_ID, AVG(r.Rating_Score) as Average_Score
            FROM Rating r
            GROUP BY r.Movie_ID
        ) AS average_ratings
        ON m.Movie_ID = average_ratings.Movie_ID
        WHERE m.Movie_ID = %s;
    """

    connection = db.get_connection()
    if not connection:
        return "Connection to database failed",500
    else:
        cursor = connection.cursor()
        cursor.execute(aggregation_query, (movie_id,))
        review_data = cursor.fetchone()
        cursor.close()
        connection.close()
        return review_data

def get_actors_in_movie_query(movie_id):
    # Query for finding the relevant actors in the movie
    actor_query = """
        SELECT 
            a.Actor_ID, 
            a.Actor_First_Name,
            a.Actor_Last_Name,
            aam.Character_Name
        FROM Actor a
        INNER JOIN Actor_And_Movie aam
        ON a.Actor_ID = aam.Actor_ID 
        INNER JOIN Movie as m
        ON aam.Movie_ID = m.Movie_ID
        WHERE m.Movie_ID = %s;
    """

    connection = db.get_connection()
    if not connection:
        return "Connection to database failed", 500
    else:
        cursor = connection.cursor()
        cursor.execute(actor_query, (movie_id,))
        actor_data = cursor.fetchall()
        cursor.close()
        connection.close()
        return actor_data

def get_directors_in_movie_query(movie_id):
    # Same as actor query, just with directors
    director_query = """
    SELECT 
        d.Director_ID,
        d.Director_First_Name,
        d.Director_Last_Name
    FROM Director d
    INNER JOIN Director_And_Movie dam
    ON d.Director_ID = dam.Director_ID
    INNER JOIN Movie m
    ON dam.Movie_ID = m.Movie_ID
    WHERE m.Movie_ID = %s;
    """

    connection = db.get_connection()

    if not connection:
        return "Connection to database failed", 500
    else:
        cursor = connection.cursor()
        cursor.execute(director_query, (movie_id,))
        director_data = cursor.fetchall()
        cursor.close()
        connection.close()
        return director_data
