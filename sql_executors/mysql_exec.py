import os
import sys
import asyncio
import json
import redis
import sentry_sdk

from datetime import date, datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling

import mysql_create_db as db_cr

sentry_sdk.init(os.environ["SENTRY_INSIGHT"])

redis_conn = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=os.getenv("REDIS_PORT", 6379),
    decode_responses=True,
    password=os.getenv("REDIS_PASSWORD", ""),
)


file_name = sys.argv[1]
fp = open(file_name)
contents = fp.read()


payload = json.loads(contents)


redis_record = redis_conn.get(payload["question"])
dbconfig = {
    "pool_name": None,
    "pool_size": 5,
    "pool_reset_session": True,
    "host": os.environ["MYSQL_HOST"],
    "user": os.environ["MYSQL_USER"],
    "passwd": os.environ["MYSQL_PASSWORD"],
    "database": str(payload["question"]),
}


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


async def fetch_records(mysql):
    try:
        mydb = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)
        con = mydb.get_connection()
        mycursor = con.cursor()
        mycursor.execute(payload["query"].upper())
        myresult = mycursor.fetchall()
        result = [
            {
                column_names.title(): item[i]
                for i, column_names in enumerate(mycursor.column_names)
            }
            for item in myresult
        ]
        result=json.dumps(result, indent=4, default=str)
        result_size=sys.getsizeof(result)
        if result_size/1024 > 500:
            print("Output too large, try add/reducing limit in query.")
        else:
            print(result)
        con.close()
    except mysql.connector.ProgrammingError as pe:
        print(pe)
    except mysql.connector.DatabaseError as de:
        print(de)
    except mysql.connector.Error as e:
        sentry_sdk.capture_message(e)
        print("Error, Please check the query!")
    except OSError as e:
        print("Output too large!")
    return None


async def main(redis_record):
    try:
        if redis_record:
            redis_conn.set(
                payload["question"], int(datetime.now().strftime("%s%f"))
            )
        else:
            # 1: Create database
            # 2: Flag in redis
            await db_cr.create_database(payload["question"], payload["url"])
            redis_conn.set(
                payload["question"], int(datetime.now().strftime("%s%f"))
            )
        await asyncio.sleep(0.1)
        await fetch_records(mysql)
        redis_conn.close()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print("Error") 
    return None


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(redis_record))
        loop.close
    except Exception as e:
        loop.close()
        print("Error") 