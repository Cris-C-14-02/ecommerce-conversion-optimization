-- =========================
-- Data Check: events_raw
-- =========================
USE ecommerce;

-- 1. Preview data
SELECT * FROM events_raw LIMIT 10;

-- 2. Table structure
DESCRIBE events_raw;

-- 3. Total rows
SELECT COUNT(*) FROM events_raw;

-- 4. Event distribution
SELECT event, COUNT(*) 
FROM events_raw
GROUP BY event;

-- 5. Null check
SELECT 
    SUM(visitorid IS NULL) AS visitorid_nulls,
    SUM(event IS NULL) AS event_nulls,
    SUM(itemid IS NULL) AS itemid_nulls
FROM events_raw;