# Индексация в MySQL

Индекс — это структура данных, предназначенная для ускорения поиска строк в таблице

Индексы снижают стоимость операций `SELECT`, но могут замедлять `INSERT`, `UPDATE`, `DELETE`, так как требуют обновления.

Создаются на один или несколько столбцов.

## Основные типы индексов в MySQL

| Тип индекса                         | Описание                                                                 |
|-------------------------------------|---------------------------------------------------------------------------|
| [`PRIMARY KEY`](#primary-key)       | Уникальный, не может содержать `NULL`. Один на таблицу.                  |
| [`UNIQUE INDEX`](#unique-index)     | Обеспечивает уникальность значений в столбце/столбцах.                   |
| [`INDEX` или `KEY`](#index)         | Обычный индекс, допускает дублирование значений.                       |
| [`FULLTEXT INDEX`](#fulltext-index) | Индекс для полнотекстового поиска (только `MyISAM`, `InnoDB` начиная с 5.6). |
| [`SPATIAL INDEX`](#spatial-index)   | Геометрические индексы (`MyISAM` и `InnoDB`), применяется к геометрическим типам. |
| [`FOREIGN KEY`](#foreign-key)       | Не индекс, но создаёт скрытый индекс на внешний ключ (для связи таблиц). |


### PRIMARY KEY

Обычно устанавливается на id:
```
ALTER TABLE employees ADD PRIMARY KEY (employee_id);
```
Если таблица уже имеет `PRIMARY KEY`, второй добавить нельзя.

### UNIQUE INDEX

Создаёт уникальный индекс. Например, запретим повторение комбинации first_name + last_name в рамках одного отдела:
```
CREATE UNIQUE INDEX uniq_name_dept ON employees (first_name, last_name, department_id);
```
### INDEX

Ускоряет поиск, сортировку, `JOIN`.

- Может быть как по одному полю:
```
CREATE INDEX idx_dept_id ON employees(department_id);
```
- Так и по нескольким полям:
```
CREATE INDEX idx_dept_salary ON employees(department_id, salary);
```

### FULLTEXT INDEX

Для полнотекстового поиска (например, по имени):
```
CREATE FULLTEXT INDEX ft_name ON employees(first_name, last_name);
```
Применим только к текстовым столбцам версии MySQL >= 5.6.

### SPATIAL INDEX

Только для географических данных, например SPATIAL INDEX(location) создаёт пространственный индекс по координатам `location`:
```
CREATE TABLE hr.employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    location POINT NOT NULL,
    SPATIAL INDEX(location)
);

--  пример для вставки:

INSERT INTO hr.employees (first_name, last_name, location)
VALUES 
('Ivan', 'Ivanov', ST_GeomFromText('POINT(40.7128 -74.0060)')), -- Нью-Йорк
('Maria', 'Petrova', ST_GeomFromText('POINT(34.0522 -118.2437)')); -- Лос-Анджелес
```


### FOREIGN KEY

Создаёт индекс автоматически:
```
ALTER TABLE employees
ADD CONSTRAINT fk_dept FOREIGN KEY (department_id) REFERENCES departments(department_id);
```
## Пример запроса и рекомендации по индексам:

Запрос:
```
SELECT first_name, last_name, department_id, salary FROM employees
WHERE department_id = 90 AND salary > 5000;
```
Рекомендуемый индекс:
```
CREATE INDEX idx_dept_salary ON employees(department_id, salary);
```
Порядок важен: `department_id` первым, именно департамент ищется по точному значению.
(поиск по неточному значению неэффективен!)
ПРОВЕРИТЬ НА EXPLAIN!!!
    Примечания

    Чем больше индекс, тем медленнее вставка.

    Всегда анализируйте запрос через EXPLAIN.

    Уникальные и первичные ключи автоматически создают индекс.