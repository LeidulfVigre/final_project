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

        query = "SELECT User_ID from User WHERE User_ID = %s"
        connection = db.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, (new_id,))
        user_data = cursor.fetchone()
        if not user_data:
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
    query = "" # tom trist string i starten
    if choose_review_rating == "1":
        query +="""SELECT m.Movie_Title, 
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
                INNER JOIN Rating r
                ON rv.Rating_ID = r.Rating_ID
                INNER JOIN Movie m 
                ON rv.Movie_ID = m.Movie_ID
                WHERE rv.User_ID = %s"""
    elif choose_review_rating == "2":
        query +=  """SELECT m.Movie_Title, 
                    m.Movie_ID,      
                    r.Rating_ID,     
                    r.Rating_Score,  
                    r.Rating_Date
            FROM Rating r
            INNER JOIN Movie m
            ON r.Movie_ID = m.Movie_ID
            WHERE r.User_ID = %s"""
    elif choose_review_rating == "3":
        query += """SELECT m.Movie_Title, 
                   m.Movie_ID,            
                   rv.Review_ID,          
                   rv.Review_Title,       
                   rv.Likes,              
                   rv.Dislikes,           
                   rv.Review_Text,        
                   r.Review_ID             
                   r.Rating_Score,        
                   r.Rating_Date 
            FROM Rating r 
            LEFT JOIN Review rv ON r.Rating_ID = rv.Rating_ID
            INNER JOIN Movie m ON r.Movie_ID = m.Movie_ID
            WHERE r.User_ID = %s"""
    
    if select_genre != "1":
        query += " AND m.Genre = %s"
    
    query += " ORDER BY r.Rating_Date"
    if order_by_date == "1":
        query += " ASC,"
    elif order_by_date == "2":
        query += " DESC,"

    query += " r.Rating_Score"    
    if order_by_score == "1":
        query += " DESC"
    elif order_by_score == "2":
        query += " ASC"
    
    query += ";"
        
    return query


