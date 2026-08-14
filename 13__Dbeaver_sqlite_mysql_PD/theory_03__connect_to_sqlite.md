**SQLite** — это лёгкая встроенная система управления базами данных (СУБД), которая хранит всю базу в одном файле.

SQLite прекрасно подходит для 
* небольших проектов, 
* обучения SQL, 
* локального хранения данных без настройки отдельного сервера.


Особенности:

* **Не требует установки сервера** — работает прямо внутри программы.
* **Данные хранятся в файле** (например, `my_database.db`).
* **Поддерживает SQL-запросы** (`SELECT`, `INSERT`, `UPDATE`, `DELETE` и др.).
* **Входит в стандартную библиотеку Python** через модуль `sqlite3`.
* **`SQLite` не имеет встроенной системы пользователей и паролей** 
  * Доступ к базе определяется правами доступа к файлу БД.


### Подключение к базе данных

Создаём подключение к SQLite.  
* Пакет `sqlite3` уже в базовой конфигурации Python (ничего дополнительно инсталлировать не надо!)
* БД тоже специально создавать не надо:
  * Если файл БД `my_database.db` ещё не существует, он будет создан автоматически.

```python
import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('my_database.db')

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()
```

### Создание таблицы

Создаём таблицу `users` для хранения информации о пользователях.

```python
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    email TEXT
);
""")

# Сохраняем изменения в базе данных
conn.commit()
```

### Добавление данных в БД

Добавляем новую запись в таблицу `users`.

```python
cursor.execute(
    "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
    ("John Doe", 25, "johndoe@example.com")
)

# Сохраняем изменения
conn.commit()
```
** ⚠️ Любые изменения данных или структуры БД ОБЯЗАТЕЛЬНО надо коммитить!**  
(Если только не настроен `autocommit=True` как на нашем школьном сервере)

### Просмотр содержимого таблицы

Получаем и выводим все записи из таблицы `users`.

```python
cursor.execute("SELECT * FROM users;")
print(cursor.fetchall())  # [(1, 'John Doe', 25, 'johndoe@example.com')]
print(cursor.fetchall()) 
```

`cursor` - это итератор.  
1. Добавление к итератору метода `fetchall()` ("извлечь всё") возвращает список тюплов
2. Итератор "одноразовый" - при повторном вызове вернёт пустой список
3. Итератор работает с циклом `for`:


```python
cursor.execute("SELECT * FROM users;")
for row in cursor:
    print(row)
```

### *Как вывести таблицу красиво?

`cursor.fetchall()` выводит только данные таблицы без заголовков.

Чтобы вывести заголовки, их сначала надо извлечь:

```python
cursor.execute("SELECT * FROM users;")
rows = cursor.fetchall()

headers = [col[0] for col in cursor.description]
```

И далее, можно воспользоваться удобным пакетом `tabulate`:
(требует предварительной инсталляции: `pip install tabulate`)

```python
from tabulate import tabulate  # pip install tabulate

print(tabulate(rows, headers=headers, tablefmt="grid"))
```