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
    



