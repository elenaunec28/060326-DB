DROP TABLE IF EXISTS tmp;

CREATE TABLE IF NOT EXISTS tmp (
	id INT PRIMARY KEY AUTO_INCREMENT,
    fixed_date DATETIME,
    flex_date TIMESTAMP
);

INSERT INTO tmp (fixed_date, flex_date)
VALUE (NOW(), NOW());

SELECT TIMEDIFF(NOW(), UTC_TIMESTAMP()) AS offset;
-- fixed_date ничем не отличается от flex_date
SELECT * FROM tmp;

-- меняем системное время в пределах сессии
SELECT @@session.time_zone;
SET time_zone = '+00:00';

-- fixed_date не изменилась, в отличии от flex_date
SELECT * FROM tmp;

SELECT TIMEDIFF(NOW(), UTC_TIMESTAMP()) AS offset;
