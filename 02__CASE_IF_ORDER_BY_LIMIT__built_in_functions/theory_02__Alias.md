# Alias (Псевдонимы) в MySQL

Alias (псевдонимы) используются для присвоения временных имен колонкам или таблицам в SQL-запросах. Это помогает сделать результаты более читаемыми или сокращать длинные имена.

## 1. Alias для колонок `AS`

Используется для переименования вывода в SELECT.

```
SELECT 
    name AS employee_name, 
    salary AS monthly_salary
FROM 
    employees;
```

* `AS` можно не писать, но с ним код читается лучше.

* Если alias содержит пробелы или спецсимволы, его берут в кавычки:
  * `SELECT name AS "Employee Name" FROM employees;`
  * (но лучше избегать пробелов в alias).

## 2. Alias для таблиц

Используется для сокращения длинных имен таблиц, особенно при `JOIN`.
```
SELECT 
    e.name, d.department_name
FROM 
    employees AS e
        JOIN 
    departments AS d ON e.department_id = d.id;
```

