import os
import asyncio
from time import sleep
import mysql.connector
from mysql.connector import Error,pooling


from urllib.request import urlopen

dbconfig = {
    "pool_name": None,
    "pool_reset_session":True,
    "pool_size": 5,
    "host": os.environ["MYSQL_HOST"],
    "user": "root",
    "passwd": os.environ["MYSQL_ROOT_PASSWORD"],
}


async def create_database(db_name, dump_query_URL):
    dump_query = urlopen(dump_query_URL).read().decode("utf-8")
    # print(dump_query)
    try:
        mydb = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)
        con = mydb.get_connection()
        mycursor = con.cursor()
        mycursor.execute("CREATE DATABASE `" + str(db_name) + "`;")
        mycursor.execute("GRANT SELECT, SHOW VIEW, PROCESS, REPLICATION CLIENT ON *.* TO '"+os.environ["MYSQL_USER"]+"'@'%' IDENTIFIED BY '"+os.environ["MYSQL_PASSWORD"]+"';")
        mycursor.execute("GRANT SELECT, SHOW VIEW, PROCESS, REPLICATION CLIENT ON *.* TO '"+os.environ["MYSQL_USER"]+"'@'localhost' IDENTIFIED BY '"+os.environ["MYSQL_PASSWORD"]+"';")
        d= await populate_database(mydb, str(db_name), dump_query)
        print("DB populated",d)
        con.close()
    except mysql.connector.Error as e:
        print(e)
    return None


async def populate_database(mydb, db_name, dump_query):
    kwargs = {"database": db_name}
    mydb.set_config(**kwargs)
    con = mydb.get_connection()
    mycursor = con.cursor()
    mycursor.execute(dump_query)
    con.commit()
    mycursor.close()
    con.close()
    sleep(0.5)
    return None
