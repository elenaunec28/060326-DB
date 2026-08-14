**Пользовательская функция**  — это сохранённая под своим именем логика, которую можно использовать в SQL-запросах, как обычную функцию (например, `NOW()`, `LENGTH()`).

Она принимает параметры, возвращает результат и вызывается внутри `SELECT`, `WHERE` и других выражений.

Их использовать, если:

    вы повторяете один и тот же расчёт в нескольких местах;

    нужно инкапсулировать сложную бизнес-логику;

    вы хотите повысить читаемость SQL-кода.

#### Синтаксис SQL-функции
```
DELIMITER //

CREATE FUNCTION имя_функции(аргументы)
RETURNS тип_возврата
DETERMINISTIC
BEGIN
    -- тело функции
    RETURN значение;
END //

DELIMITER ;
```
Пояснения:

    `DELIMITER` нужен, чтобы отличить конец функции от обычной точки с запятой внутри тела.

    `RETURNS` — указывает тип возвращаемого значения.

    `DETERMINISTIC` — означает, что функция всегда возвращает один и тот же результат при одинаковых входных данных.

#### Пример: функция, возвращающая сумму с НДС 20%
```
DELIMITER //

CREATE FUNCTION add_vat(price DECIMAL(10, 2))
RETURNS DECIMAL(10, 2)
DETERMINISTIC 
BEGIN
    RETURN price * 1.2;
END //

DELIMITER ;
```
Использование:
```
SELECT name, add_vat(price) AS price_with_vat FROM products;
```
#### Пример 2: функция, проверяющая, чётное ли число
```
DELIMITER //

CREATE FUNCTION is_even(n INT)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    RETURN MOD(n, 2) = 0;
END //

DELIMITER ;
```
Пример:
```
SELECT id FROM users WHERE is_even(id);
```
#### Просмотр и удаление функций

Посмотреть список:
```
SHOW FUNCTION STATUS WHERE Db = 'имя_БД_где_создана_функция';
```
Удалить функцию:
```
DROP FUNCTION имя_функции;
```