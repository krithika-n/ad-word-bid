#!/usr/bin/python
from dbConnect import *

def pg_load_table(file_path, table_name, conn):
    '''
    uploads csv to a target table
    '''
    try:
        cur = conn.cursor()
        f = open(file_path, "r")
        cur.copy_expert("copy {} from STDIN CSV HEADER QUOTE '\"'".format(table_name), f)
        cur.execute("commit;")
        print("Loaded data into {}".format(table_name))

    except Exception as e:
        print("Error: {}".format(str(e)))
        sys.exit(1)

def fill_Tables(conn, folder_path):
    '''
    inserts values from CSV files in folder_path into the table in database connected to conn
    '''
    #fill table Inventory_current_onsite
    file_path = folder_path + "/Inventory_Current_Onsite.csv"
    table_name = "inventory_current_onsite"
    pg_load_table(file_path, table_name, conn)

    # fill table inventory_historical
    file_path = folder_path + "/Inventory_Historical.csv"
    table_name = "inventory_historical"
    pg_load_table(file_path, table_name, conn)

    # fill table kw_attributes
    file_path = folder_path + "/KW_Attributes.csv"
    table_name = "kw_attributes"
    pg_load_table(file_path, table_name, conn)

    #fill table kw_performance
    file_path = folder_path + "/KW_Performance_L120D.csv"
    table_name = "kw_performance"
    pg_load_table(file_path, table_name, conn)

    # fill table make_model_asr
    file_path = folder_path + "/Make_Model_ASR.csv"
    table_name = "make_model_asr"
    pg_load_table(file_path, table_name, conn)

def create_aggregates(conn):
    '''
    creates aggregates tables in the database by executing queries in aggregate.sql
    '''
    cursor = conn.cursor()
    cursor.execute(open("aggregate.sql", "r").read())
    
def main():
    if len(sys.argv) < 4:
        print "Specify folder path, postgres username and password as argument."
        sys.exit(1)

    dbname = 'carvana'
    host = 'localhost'
    user = sys.argv[2]
    pwd = sys.argv[3]
    conn = connect_to_db(dbname, host, user, pwd)
    folder_path = sys.argv[1]
    fill_Tables(conn, folder_path)
    create_aggregates(conn)
    close_connection_db(conn)
    

if __name__ == "__main__":
    main()
