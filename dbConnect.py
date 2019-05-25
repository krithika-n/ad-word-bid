#!/usr/bin/python
import psycopg2
import sys

def connect_to_db(dbname, host, user, pwd):
    '''
        creates and returns a connection to database
    '''
    try:
        conn = psycopg2.connect(dbname=dbname, host=host, user=user, password=pwd)
        return conn

    except Exception as e:
        print("Error: {}".format(str(e)))
        sys.exit(1)

def close_connection_db(conn):
    '''
        closes the connection to database in conn
    '''
    try:
        conn.close()
        #print("DB connection closed.")

    except Exception as e:
        print("Error: {}".format(str(e)))
        sys.exit(1)
