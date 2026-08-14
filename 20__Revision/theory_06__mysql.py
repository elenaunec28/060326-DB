from pprint import pprint

import mysql.connector
from local_settings import dbconfig

with mysql.connector.connect(**dbconfig) as connection:

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM sakila.film LIMIT 10")

        print("--- Структура таблицы ------------------------")
        pprint(cursor.description)

        print("--- Список тюплов ------------------------")
        print(*cursor.fetchall(), sep='\n')

    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM sakila.film LIMIT 10")

        print("--- Список словарей ------------------------")
        pprint(cursor.fetchall())
