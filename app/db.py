import mysql.connector

def get_connection():
    try:
        mydb = mysql.connector.connect(
            host="localhost:3306",
            user="root",
            password="123",
            database="LSMDb"
        )
        return mydb
    except mysql.connector.Error as err:
        print("Error connecting to database: ", err)
        return None