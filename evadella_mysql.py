import mysql.connector
import os

class db_instance:
    
    mysql_host = os.environ.get('localhost')
    mysql_user = os.environ.get('root')
    mysql_password = os.environ.get('Avatar*9164')
    mysql_database = os.environ.get('ecomm')

    try:
    # Establish the connection
        mydb = mysql.connector.connect(
            port = 3306,
            user = "root",
            password = "Avatar*9164",
            database = "ecomm",
            sql_mode=""
        )
    
    except:
        raise NameError("improper DB connection, check the connection attributes in evadella_mysql file")
    
    cursor = mydb.cursor()

    # change the default SQL mode from 'ONLY_FULL_GROUP_BY'
    sql_mode = ""
    cursor.execute("SET SESSION sql_mode = %s", (sql_mode,))

    mydb.commit()
    cursor.close()

    def __init__(self):
        pass    