**Учебный пример на MySQL** — Автоплатежи через триггеры

Мы создадим минимальную модель с тремя таблицами и реализуем логику:

- При добавлении платежа (`payments`) → увеличивается баланс пользователя.
- Автоматически пытаемся оплатить **pending** заказы (по порядку создания).
- Логика "жадная": оплачиваем то, на что хватает денег (даже если пропускаем дорогой заказ).

---

### 1. Создание таблиц и объектов

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    balance DECIMAL(10,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('cart', 'pending', 'paid') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

```sql
-- =========================
-- 2. Хранимая процедура автоплатежа
-- =========================
DROP PROCEDURE IF EXISTS auto_pay_pending_orders;

DELIMITER $$

CREATE PROCEDURE auto_pay_pending_orders(IN p_user_id INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_order_id INT;
    DECLARE v_order_amount DECIMAL(10,2);
    DECLARE v_current_balance DECIMAL(10,2);

    -- Курсор только по "pending" заказам (отсортированы по дате создания)
    DECLARE cur CURSOR FOR
        SELECT id, amount 
        FROM orders 
        WHERE user_id = p_user_id 
          AND status = 'pending'
        ORDER BY created_at ASC;

	-- Если заказов больше нет — цикл заканчивается:
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE; 

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_order_id, v_order_amount;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Получаем текущий баланс
        SELECT balance INTO v_current_balance 
        FROM users 
        WHERE id = p_user_id;

        -- Если хватает денег — оплачиваем
        IF v_current_balance >= v_order_amount THEN
            
            UPDATE orders 
            SET status = 'paid' 
            WHERE id = v_order_id;

            UPDATE users 
            SET balance = balance - v_order_amount 
            WHERE id = p_user_id;

        END IF;

    END LOOP;

    CLOSE cur;
END$$

DELIMITER ;
```

```sql
-- =========================
-- 3. Триггер
-- =========================

-- Триггер при добавлении платежа
DROP TRIGGER IF EXISTS trg_payments_after_insert;

DELIMITER $$
CREATE TRIGGER trg_payments_after_insert
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    -- Увеличиваем баланс
    UPDATE users 
    SET balance = balance + NEW.amount 
    WHERE id = NEW.user_id;

    -- Запускаем автоплатеж
    CALL auto_pay_pending_orders(NEW.user_id);
END$$
DELIMITER ;
```

---

### 2. Заполнение тестовыми данными

```sql
-- Создаём пользователя
INSERT INTO users (balance) VALUES (0);

-- Создаём 3 pending заказа (150, 60, 20)
INSERT INTO orders (user_id, amount, status, created_at) VALUES
(1, 150.00, 'pending', '2026-06-01 10:00:00'),
(1, 60.00,  'pending', '2026-06-02 10:00:00'),
(1, 20.00,  'pending', '2026-06-03 10:00:00');

-- И проверяем состояние БД
SELECT * FROM users;
SELECT * FROM orders;
SELECT * FROM payments;
```

**Текущее состояние:**
- Баланс пользователя: **0**
- 3 заказа в статусе `pending`: 150, 60, 20

---

### 3. Добавляем оплату 100

```sql
INSERT INTO payments (user_id, amount) VALUES (1, 100.00);
    
-- И проверяем состояние БД
SELECT * FROM users;
SELECT * FROM orders;
SELECT * FROM payments;
```

---

### 4. Результат после добавления платежа

**Ожидаемый результат:**

| id | amount | status      | created_at          | Комментарий                  |
|----|--------|-------------|---------------------|------------------------------|
| 1  | 150.00 | **pending** | 2026-06-01 10:00:00 | **Не оплачен** (не хватило) |
| 2  | 60.00  | **paid**    | 2026-06-02 10:00:00 | **Оплачен**                  |
| 3  | 20.00  | **paid**    | 2026-06-03 10:00:00 | **Оплачен**                  |

**Баланс пользователя после операции:**

```sql
balance = 100 - 60 - 20 = **20.00**
```

---

### Итоговая картина

| Действие                    | Что произошло                                      | Результат                  |
|----------------------------|----------------------------------------------------|----------------------------|
| Добавлен платёж **100**    | Баланс увеличен на 100                             | Баланс = 100               |
| Автоплатеж (жадный)        | Оплачены заказы, на которые хватило денег          | Оплачены заказы 60 и 20    |
| Итоговый баланс            | 100 - 60 - 20                                      | **20.00**                  |
| Статус заказов             | Заказ 150 остался `pending`                        | Ждёт следующего пополнения |

---

### Дополнительно: Как работает логика

- Триггер на `payments` увеличивает баланс.
- Затем вызывается процедура `auto_pay_pending_orders`, которая проходит по заказам **по порядку создания**.
- Если на заказ хватает денег — он оплачивается и баланс уменьшается.
- Если не хватает — заказ **пропускается** (жадная стратегия).


### Выводы
| Критерий                                                     | Оценка               |
|--------------------------------------------------------------|----------------------|
| Учебный пример SQL-процедур и триггеров                      | Отличный             |
| Небольшой внутренний проект                                  | Допустимо            |
| Типичный Python/FastAPI/Django проект                        | Спорно               |
| Производительность на малых объёмах                          | Отличная             |
| Производительность на больших объёмах                        | Ограничена курсорами |
| Прозрачность бизнес-логики                                   | Низкая               |
| Возможность дебагинга                                        | Ограниченная         |
| Риск блокировок и race conditions                            | Повышенный           |
| Тестируемость                                                | Низкая               |
| Переносимость между СУБД                                     | Низкая               |
| Централизация логики (невозможно забыть вызвать авто-оплату) | Высокая              |