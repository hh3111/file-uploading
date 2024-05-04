import os
import pymysql
from flask import jsonify

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

def open_connection():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user,
                                   password=db_password,
                                   unix_socket=unix_socket,
                                   db=db_name,
                                   cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        return e
    return conn

def get(username, password):
    conn = open_connection()
    with conn.cursor() as cursor:
        result = cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s',
                        (username, password))
        users = cursor.fetchall()
        if result > 0:
            got_users = (users)
        else:
            got_users = None
        return got_users

def create(username, password):
    conn = open_connection()
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)',
                        (username, password))
    conn.commit()
    conn.close()