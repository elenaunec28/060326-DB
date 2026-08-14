В MySQL процедуры (или хранимые процедуры) — это набор SQL-инструкций,  
которые сохраняются в базе данных и могут быть вызваны по имени. 

**Процедура (или Хранимая процедура)** — это подпрограмма, сохранённая в базе данных,  
которую можно вызывать многократно с определёнными параметрами.

- Компилируется при создании (CREATE PROCEDURE).
- Хранится в метаданных конкретной БД, как исполняемый объект.
- При CALL выполнение идёт быстрее обычного запроса, 
  - т.к. основная логика уже "подготовлена" компиляцией и уже находится на сервере

Сравнение процедуры и функции:

| Характеристика                     | Процедура (PROCEDURE)                    | Функция (FUNCTION)                      |
|------------------------------------|------------------------------------------|-----------------------------------------|
| **Назначение**                     | Выполнение действий                      | Вычисление и возврат значения           |
| **Возвращает значение**            | Если использовуется `OUT` и/или `INOUT`) | ✅ Всегда (обязательно `RETURN`)        |
| **Вызывается как**                 | `CALL имя(...)`                          | `SELECT имя(...)`                       |
| **Можно использовать в SELECT**    | ❌ Нет                                    | ✅ Да                                    |
| **Типы параметров**                | `IN`, `OUT`, `INOUT`                     | Только `IN`                             |
| **Может изменять данные в БД**     | ✅ Да (`INSERT`, `UPDATE`, `DELETE`)      | ❌ Нет (изменения запрещены)             |
| **Где используется**               | В SQL-скриптах, приложениях              | В выражениях, SELECT, WHERE, ORDER BY   |
| **Обязателен ли RETURN**           | ❌ Нет                                    | ✅ Да                                    |
| **Можно ли использовать DML?**     | ✅ Да                                     | ❌ Нет (в MySQL - нет)                   |
| **Сфера применения**               | Автоматизация операций, бизнес-логика    | Вычисления, преобразование данных       |
| **Где хранится**                   | В конкретной базе данных (`mysql.proc`)  | В конкретной базе данных (`mysql.proc`) |
| **Экспорт через mysqldump**        | Нужно флаг `--routines`                  | Нужно флаг `--routines`                 |
| **Можно ли использовать в триггере**| ✅ Да                                     | ✅ Да (но с ограничениями)               |


## Процедура без параметров

*Создаём процедуру, которая выводит список всех сотрудников:
```
DELIMITER //

CREATE PROCEDURE GetAllEmployees()
BEGIN
    SELECT first_name, last_name FROM employees;
END //

DELIMITER ;
```
Вызов процедуры:
```
CALL GetAllEmployees();
```

### Сравнение PROCEDURE и VIEW

| Критерий                                            | `PROCEDURE GetAllEmployees()`             | `VIEW all_employees`                        |
|-----------------------------------------------------|-------------------------------------------|---------------------------------------------|
| **Назначение**                                      | Выполняет действия                        | Представляет данные                         |
| **Можно вызывать как**                              | `CALL GetAllEmployees()`                  | `SELECT * FROM all_employees`               |
| **Возвращает**                                      | Результат SELECT                          | Результат SELECT                            |
| **Можно ли фильтровать?**                           | ❌ Нет (`WHERE` нельзя применить к `CALL`) | ✅ Да (`WHERE`, `ORDER BY`, `LIMIT` и т.д.)  |
| **Можно ли использовать в JOIN?**                   | ❌ Нет                                     | ✅ Да                                        |
| **Можно ли использовать как часть SQL-запроса?**    | ❌ Нет — `CALL` нельзя встроить в `SELECT` | ✅ Да — можно использовать как таблицу       |
| **Гибкость**                                        | ✅ Можно включать переменные, IF, циклы    | ❌ Только SELECT-запрос                      |
| **Изменяет данные?** (`INSERT`, `UPDATE`, `DELETE`) | ✅ Может (в других процедурах)       | ❌ Нет                                       |
| **Оптимизация**                                     | ❌ Нет (выполняется как отдельный запрос)  | ✅ Да (оптимизируется как часть SQL-запроса) |



## Процедура с параметрами

### 1. Процедура с параметром IN

Параметр IN — входной, его передают при вызове.
```
DELIMITER //

CREATE PROCEDURE GetEmployeesByDepartment(IN dept_id INT)
BEGIN
    SELECT first_name, last_name
    FROM employees
    WHERE department_id = dept_id;
END //

DELIMITER ;
```
Использование:
```
CALL GetEmployeesByDepartment(3);
```

### 2. Процедура с параметром OUT

*Параметр OUT — выходной, процедура запишет в него значение, которое можно получить после вызова.*
```
DELIMITER //

CREATE PROCEDURE CountEmployeesByDepartment(IN dept_id INT, OUT emp_count INT)
BEGIN
    SELECT COUNT(*) INTO emp_count
    FROM employees
    WHERE department_id = dept_id;
END //

DELIMITER ;
```
Использование:
```
CALL CountEmployeesByDepartment(3, @count);
SELECT @count;
```
ПРИМЕЧАНИЕ:
Переменная `@count` — это `user-defined session variable` (пользовательская сессионная переменная)
Создаётся автоматически, при вызове процедуры.

Её  можно создать и заранее (но делать это совсем не обязательно!)
```
SET  @count = 0;
CALL CountEmployeesByDepartment(3, @count);
SELECT @count;
```

### 3. Процедура с параметром INOUT

*Параметр INOUT — и входной, и выходной, может передавать значение в процедуру и получать изменённое обратно.*

```
DELIMITER //

CREATE PROCEDURE IncreaseSalaryByPercent(INOUT percent_increase DECIMAL(5,2))
BEGIN
    UPDATE employees
    SET salary = salary * (1 + percent_increase / 100) LIMIT 300;

    -- Например, вернуть новое значение процента (умножим на 2 для демонстрации)
    SET percent_increase = percent_increase * 2;
END //

DELIMITER ;
```
Использование:
```
SET @pct = 5.0;
CALL IncreaseSalaryByPercent(@pct);
SELECT @pct;  -- теперь будет 10.0
```

### ⚠️ Возможная проблема с переменной (IN и/или INOUT)

Если ошибочно запустить процедуру с неопределённым параметром,  
то это может уничтожить данные в таблице.  
(Поскольку NULL в формуле делает результат тоже NULL)

Пример:
```
CALL IncreaseSalaryByPercent(@unknown);
SELECT @unknown;  -- теперь будет NULL
SELECT * FROM employees;  -- теперь NULL будет и в каждой зарплате
```

Решение:
Проверять IN или INOUT переменную в самой процедуре:

```mysql
DELIMITER //

CREATE PROCEDURE SafeIncreaseSalaryByPercent(INOUT percent_increase DECIMAL(5,2))
BEGIN
    -- Проверяем, передано ли значение (NULL или 0)
    IF percent_increase IS NULL THEN
        SET percent_increase = 0.00; -- т.е. не увеличиваем
    END IF;
    
    UPDATE employees
    SET salary = salary * (1 + percent_increase / 100) LIMIT 300;

    -- Например, вернуть новое значение процента (умножим на 2 для демонстрации)
    SET percent_increase = percent_increase * 2;
END //

DELIMITER ;
```


### Процедура, создающая временную таблицу
```
DELIMITER //

CREATE PROCEDURE get_employee_salaries(IN emp_id INT)
BEGIN
    -- Удаляем временную таблицу, если она уже есть
    DROP TEMPORARY TABLE IF EXISTS temp_salaries;

    -- Создаём временную таблицу и наполняем результатом
    CREATE TEMPORARY TABLE temp_salaries AS
    SELECT employee_id, salary
    FROM employees
    WHERE employee_id > emp_id;
END //

DELIMITER ;
```

Создание таблицы и её вызов:
```
CALL get_employee_salaries(100);
SELECT * FROM temp_salaries;
```

ВАЖНО: ⚠️ временная таблица будет существовать ТОЛЬКО в текущей сессии!

## ❌ Удаление процедуры
```
DROP PROCEDURE IF EXISTS GetAllCities;
```

## Получить список функций и процедур конкретной БД

```
SELECT 
    ROUTINE_NAME, ROUTINE_TYPE
FROM 
    INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'database_name';
```

## Узнать содержимое функции/процедуры

```
SHOW CREATE FUNCTION function_name;
SHOW CREATE PROCEDURE procedure_name;
```
