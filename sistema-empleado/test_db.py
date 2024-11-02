import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='sistema2'
)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        result = cursor.fetchone()
        print("Database version: {}".format(result))
finally:
    connection.close()
