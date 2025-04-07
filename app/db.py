import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost:3306",
        user="root",
        password="123",
        database="LSMDb"
    )