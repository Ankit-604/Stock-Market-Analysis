-- =====================================================================
-- Stock Market Analysis in SQL  |  MySQL 8.0+
-- Six NSE stocks, 2015-01-01 to 2018-07-31 (889 trading days each)
-- Run top to bottom on a fresh database; every CREATE is preceded by DROP IF EXISTS.
-- =====================================================================

-- [MYSQL-ONLY-START]
CREATE DATABASE IF NOT EXISTS stock_analysis;
USE stock_analysis;
-- Enable first:  SET GLOBAL local_infile = 1;  (and OPT_LOCAL_INFILE=1 in Workbench)

-- ---------------------------------------------------------------------
-- SETUP: load the six CSVs (dates like 31-July-2018 -> DATE, blanks -> NULL)
-- Change /path/to/ to the folder holding the CSV files.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS bajaj_auto;
CREATE TABLE bajaj_auto (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
DROP TABLE IF EXISTS eicher_motors;  CREATE TABLE eicher_motors  LIKE bajaj_auto;
DROP TABLE IF EXISTS hero_motocorp;  CREATE TABLE hero_motocorp  LIKE bajaj_auto;
DROP TABLE IF EXISTS infosys;        CREATE TABLE infosys        LIKE bajaj_auto;
DROP TABLE IF EXISTS tcs;            CREATE TABLE tcs            LIKE bajaj_auto;
DROP TABLE IF EXISTS tvs_motors;     CREATE TABLE tvs_motors     LIKE bajaj_auto;

LOAD DATA LOCAL INFILE '/path/to/Bajaj_Auto.csv' INTO TABLE bajaj_auto
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

LOAD DATA LOCAL INFILE '/path/to/Eicher_Motors.csv' INTO TABLE eicher_motors
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

LOAD DATA LOCAL INFILE '/path/to/Hero_Motocorp.csv' INTO TABLE hero_motocorp
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

LOAD DATA LOCAL INFILE '/path/to/Infosys.csv' INTO TABLE infosys
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

LOAD DATA LOCAL INFILE '/path/to/TCS.csv' INTO TABLE tcs
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

LOAD DATA LOCAL INFILE '/path/to/TVS_Motors.csv' INTO TABLE tvs_motors
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');
-- [MYSQL-ONLY-END]

-- =====================================================================
-- PART 1: GET TO KNOW THE DATA
-- =====================================================================

-- Task 1: how much history? (expect 889 | 2015-01-01 | 2018-07-31)
SELECT COUNT(*)  AS trading_days,
       MIN(date) AS first_day,
       MAX(date) AS last_day
FROM bajaj_auto;

-- Task 2: Eicher's five best closes (top > 32,000; all in the same month)
SELECT date, close_price
FROM eicher_motors
ORDER BY close_price DESC
LIMIT 5;

-- Task 3: TCS average close by year (2016 = 2419.00; 2018 has only 7 months)
SELECT YEAR(date) AS year,
       ROUND(AVG(close_price), 2) AS avg_close
FROM tcs
GROUP BY YEAR(date)
ORDER BY YEAR(date);

-- Task 4: find the holes (NULL deliverable_qty) across all six tables
SELECT 'bajaj_auto' AS stock, date FROM bajaj_auto    WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'eicher_motors',       date FROM eicher_motors WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'hero_motocorp',       date FROM hero_motocorp WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'infosys',             date FROM infosys       WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tcs',                 date FROM tcs           WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tvs_motors',          date FROM tvs_motors    WHERE deliverable_qty IS NULL;

-- =====================================================================
-- PART 2: THE ASSIGNMENT
-- =====================================================================

-- Task 5: moving averages for Bajaj Auto -> bajaj1
-- 20-day window = 19 PRECEDING + current row; NULL until a full window exists.
DROP TABLE IF EXISTS bajaj1;
CREATE TABLE bajaj1 AS
SELECT
  date,
  close_price,
  CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20
       THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
  END AS ma20,
  CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50
       THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
  END AS ma50
FROM bajaj_auto;

-- Task 6: master table, one row per date, all six closing prices
DROP TABLE IF EXISTS master_table;
CREATE TABLE master_table AS
SELECT b.date,
       b.close_price AS bajaj,
       t.close_price AS tcs,
       v.close_price AS tvs,
       i.close_price AS infosys,
       e.close_price AS eicher,
       h.close_price AS hero
FROM bajaj_auto b
JOIN tcs           t ON t.date = b.date
JOIN tvs_motors    v ON v.date = b.date
JOIN infosys       i ON i.date = b.date
JOIN eicher_motors e ON e.date = b.date
JOIN hero_motocorp h ON h.date = b.date;

-- Task 7: golden-cross signals for Bajaj Auto -> bajaj2
-- Buy  = ma20 crosses ABOVE ma50 today (yesterday ma20 <= ma50)
-- Sell = ma20 crosses BELOW ma50 today (yesterday ma20 >= ma50)
-- NULL guard first: any missing average today or yesterday -> Hold.
DROP TABLE IF EXISTS bajaj2;
CREATE TABLE bajaj2 AS
WITH t AS (
  SELECT date, close_price, ma20, ma50,
         LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
         LAG(ma50) OVER (ORDER BY date) AS prev_ma50
  FROM bajaj1
)
SELECT date, close_price,
  CASE
    WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
    WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
    WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
    ELSE 'Hold'
  END AS `signal`
FROM t;

-- Task 8: how often did it trigger? (expect Buy 12, Hold 866, Sell 11)
SELECT `signal`, COUNT(*) AS days
FROM bajaj2
GROUP BY `signal`
ORDER BY `signal`;

-- Task 9: signal on a given day (expect 'Buy' for 2018-06-21)
SELECT `signal` FROM bajaj2 WHERE date = '2018-06-21';

-- [MYSQL-ONLY-START]
DROP FUNCTION IF EXISTS bajaj_signal;
DELIMITER $$
CREATE FUNCTION bajaj_signal(d DATE)
RETURNS VARCHAR(4) DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE s VARCHAR(4);
  SELECT `signal` INTO s FROM bajaj2 WHERE date = d;
  RETURN s;               -- NULL if the market was closed that day
END $$
DELIMITER ;

SELECT bajaj_signal('2015-05-18');   -- Buy
SELECT bajaj_signal('2018-06-21');   -- Buy
-- [MYSQL-ONLY-END]

-- Task 10: all six stocks in one query (unrounded averages, partitioned windows)
WITH prices AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL SELECT 'Eicher Motors',  date, close_price FROM eicher_motors
  UNION ALL SELECT 'Hero Motocorp',  date, close_price FROM hero_motocorp
  UNION ALL SELECT 'Infosys',        date, close_price FROM infosys
  UNION ALL SELECT 'TCS',            date, close_price FROM tcs
  UNION ALL SELECT 'TVS Motors',     date, close_price FROM tvs_motors
),
ma AS (
  SELECT stock, date, close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM prices
),
lagged AS (
  SELECT stock, date, close_price, ma20, ma50,
         LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20,
         LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50
  FROM ma
),
sig AS (
  SELECT stock, date, close_price,
    CASE
      WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
      WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
      WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
      ELSE 'Hold'
    END AS `signal`
  FROM lagged
),
latest AS (
  SELECT stock, date, `signal`,
         ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date DESC) AS rn
  FROM sig
  WHERE `signal` <> 'Hold'
)
SELECT s.stock,
       SUM(s.`signal` = 'Buy')  AS buys,
       SUM(s.`signal` = 'Sell') AS sells,
       l.date     AS last_signal_date,
       l.`signal` AS last_signal
FROM sig s
JOIN latest l ON l.stock = s.stock AND l.rn = 1
GROUP BY s.stock, l.date, l.`signal`
ORDER BY s.stock;

-- =====================================================================
-- PART 3: QUESTION THE RESULT
-- =====================================================================

-- Task 11: who went up? First vs last close (raw prices)
WITH prices AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL SELECT 'Eicher Motors',  date, close_price FROM eicher_motors
  UNION ALL SELECT 'Hero Motocorp',  date, close_price FROM hero_motocorp
  UNION ALL SELECT 'Infosys',        date, close_price FROM infosys
  UNION ALL SELECT 'TCS',            date, close_price FROM tcs
  UNION ALL SELECT 'TVS Motors',     date, close_price FROM tvs_motors
),
ends AS (
  SELECT stock, MIN(date) AS first_d, MAX(date) AS last_d
  FROM prices GROUP BY stock
)
SELECT e.stock,
       f.close_price AS first_close,
       l.close_price AS last_close,
       ROUND(100.0 * (l.close_price - f.close_price) / f.close_price, 1) AS pct_change
FROM ends e
JOIN prices f ON f.stock = e.stock AND f.date = e.first_d
JOIN prices l ON l.stock = e.stock AND l.date = e.last_d
ORDER BY pct_change DESC;

-- Task 12: the data trap - each stock's single worst day
-- Infosys 2015-06-15 (-49.9%) and TCS 2018-05-31 (-50.4%) are 1:1 bonus issues, not crashes.
WITH prices AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL SELECT 'Eicher Motors',  date, close_price FROM eicher_motors
  UNION ALL SELECT 'Hero Motocorp',  date, close_price FROM hero_motocorp
  UNION ALL SELECT 'Infosys',        date, close_price FROM infosys
  UNION ALL SELECT 'TCS',            date, close_price FROM tcs
  UNION ALL SELECT 'TVS Motors',     date, close_price FROM tvs_motors
),
moves AS (
  SELECT stock, date, close_price,
         100.0 * (close_price / LAG(close_price) OVER (PARTITION BY stock ORDER BY date) - 1) AS pct_move
  FROM prices
),
ranked AS (
  SELECT stock, date, close_price, pct_move,
         ROW_NUMBER() OVER (PARTITION BY stock ORDER BY pct_move) AS rn
  FROM moves
  WHERE pct_move IS NOT NULL
)
SELECT stock, date, close_price, ROUND(pct_move, 1) AS pct_move
FROM ranked
WHERE rn = 1
ORDER BY pct_move;

-- Task 13: fix it - adjust for the two 1:1 bonus issues (divide pre-event prices by 2)
WITH adjusted AS (
  SELECT 'TCS' AS stock, date,
         CASE WHEN date < '2018-05-31' THEN close_price / 2 ELSE close_price END AS adj_close
  FROM tcs
  UNION ALL
  SELECT 'Infosys', date,
         CASE WHEN date < '2015-06-15' THEN close_price / 2 ELSE close_price END
  FROM infosys
)
SELECT stock,
       ROUND(100.0 * (MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) /
                      MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) - 1), 1) AS adjusted_pct_change
FROM adjusted
WHERE date BETWEEN '2015-01-01' AND '2018-07-31'
GROUP BY stock
ORDER BY stock;

-- Stretch (Task 14): rebuild signals for all six stocks on ADJUSTED prices.
-- Expect TCS 12/12 with last signal Buy 2018-04-20; Infosys 10/10, last Buy 2018-05-07.
WITH prices AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL SELECT 'Eicher Motors',  date, close_price FROM eicher_motors
  UNION ALL SELECT 'Hero Motocorp',  date, close_price FROM hero_motocorp
  UNION ALL SELECT 'Infosys',        date, close_price FROM infosys
  UNION ALL SELECT 'TCS',            date, close_price FROM tcs
  UNION ALL SELECT 'TVS Motors',     date, close_price FROM tvs_motors
),
adj AS (
  SELECT stock, date,
         CASE WHEN stock = 'TCS'     AND date < '2018-05-31' THEN close_price / 2
              WHEN stock = 'Infosys' AND date < '2015-06-15' THEN close_price / 2
              ELSE close_price END AS close_price
  FROM prices
),
ma AS (
  SELECT stock, date, close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM adj
),
lagged AS (
  SELECT stock, date, close_price, ma20, ma50,
         LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20,
         LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50
  FROM ma
),
sig AS (
  SELECT stock, date, close_price,
    CASE
      WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
      WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
      WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
      ELSE 'Hold'
    END AS `signal`
  FROM lagged
),
latest AS (
  SELECT stock, date, `signal`,
         ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date DESC) AS rn
  FROM sig WHERE `signal` <> 'Hold'
),
ends AS (SELECT stock, MIN(date) AS first_d, MAX(date) AS last_d FROM adj GROUP BY stock)
SELECT s.stock,
       SUM(s.`signal` = 'Buy')  AS buys,
       SUM(s.`signal` = 'Sell') AS sells,
       l.date AS last_signal_date, l.`signal` AS last_signal,
       ROUND(100.0 * (MAX(CASE WHEN s.date = e.last_d  THEN s.close_price END) /
                      MAX(CASE WHEN s.date = e.first_d THEN s.close_price END) - 1), 1) AS adjusted_pct_change
FROM sig s
JOIN latest l ON l.stock = s.stock AND l.rn = 1
JOIN ends   e ON e.stock = s.stock
GROUP BY s.stock, l.date, l.`signal`
ORDER BY s.stock;
