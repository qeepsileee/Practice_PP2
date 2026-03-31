import psycopg2
from config import config

def connect():
    return psycopg2.connect(**config)