import mysql.connector
import time

from local_settings import dbconfig


def execute_query(cursor, query):
    """Функция выполняет запрос query
    и возвращает время его выполнения в секундах.
    """
    start = time.time()
    cursor.execute(query)
    _ = cursor.fetchall()  # загружаем все результаты
    end = time.time()
    return end - start

def average_query_time(cursor, query, runs=10):
    """Функция повторяет запрос query runs раз
    И возвращает усреднённое время выполнения каждого запроса
    """
    times = []
    for _ in range(runs):
        t = execute_query(cursor, query)
        times.append(t)
    return sum(times) / len(times)

def main():
    query1 = "SELECT SQL_NO_CACHE age FROM testdb.big_table WHERE age = 30;"
    query2 = "SELECT SQL_NO_CACHE * FROM testdb.big_table WHERE age = 30;"
    drop_index = "DROP INDEX idx_big_table_age ON testdb.big_table;"

    with mysql.connector.connect(**dbconfig) as conn:
        with conn.cursor() as cursor:
            print("""
            Внимание!!!
            Перед выполнением скрипта необходимо создать индекс:
            CREATE INDEX idx_big_table_age ON testdb.big_table(age);
            """)

            print("Разогрев кэша...")
            cursor.execute(query1)
            cursor.fetchall()

            print("⏱ Выполняем запросы с индексом...")
            avg_with_index1 = average_query_time(cursor, query1)
            print(f"Среднее время с индексом для query1: {avg_with_index1:.6f} сек")
            avg_with_index2 = average_query_time(cursor, query2)
            print(f"Среднее время с индексом для query2: {avg_with_index2:.6f} сек")

            print("🧹 Удаляем индекс...")
            cursor.execute(drop_index)
            conn.commit()

            print("⏱ Выполняем запросы без индекса...")
            avg_without_index1 = average_query_time(cursor, query1)
            print(f"Среднее время без индекса для query1: {avg_without_index1:.6f} сек")
            avg_without_index2 = average_query_time(cursor, query2)
            print(f"Среднее время без индекса для query2: {avg_without_index2:.6f} сек")

            print(f"Выигрыш индексации для query1: {avg_without_index1 / avg_with_index1:.2f}")
            print(f"Выигрыш индексации для query2: {avg_without_index2 / avg_with_index2:.2f}")

if __name__ == "__main__":
    main()
