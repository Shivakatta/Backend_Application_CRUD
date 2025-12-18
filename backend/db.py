import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Shiva@366",
    "database": "users_data",
    "connection_timeout": 5,
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)
