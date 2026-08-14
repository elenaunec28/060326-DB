"""
Пакет mysql.connector внешней, поэтому требует предварительной инсталляции:

pip install mysql-connector-python

Кроме того, требуется сохранить в отдельном файле local_settings.py параметры подключения
"""

import mysql.connector
from local_settings import dbconfig


connection = mysql.connector.connect(**dbconfig)

cursor = connection.cursor()


# Получение списка таблиц
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

# Вывод списка таблиц
print("Список таблиц в базе данных sakila:")
for table in tables:
    print(table[0])


print("Список жанров из БД sakila:")
cursor.execute("SELECT * FROM category;")
for id, genre, *_ in cursor:
    print(id, genre)