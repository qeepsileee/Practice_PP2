import psycopg2
from config import config

def connect():
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print("Error:", e)