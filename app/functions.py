"""
File with helper functions
"""
from werkzeug.security import generate_password_hash, check_password_hash

# Function for checking a valid login.
def check_login(provided_password, stored_password):
    
    if check_password_hash(stored_password, provided_password):
        return True
    else:
        return False
  
# Function for hashing a password for a new user 
def hash_password(provided_password):
    return generate_password_hash(provided_password)

