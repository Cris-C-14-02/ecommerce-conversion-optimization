USE ecommerce;

-- =========================
-- Feature Engineering
-- =========================

DROP TABLE IF EXISTS user_features;

CREATE TABLE user_features (
    visitorid BIGINT,
    view_count INT,
    cart_count INT,
    purchase_count INT,
    has_viewed TINYINT,
    has_carted TINYINT,
    has_purchased TINYINT,
    view_to_cart_rate DOUBLE,
    cart_to_purchase_rate DOUBLE,
    label_purchase TINYINT
);

CREATE INDEX idx_visitorid_event ON events_raw(visitorid, event);

INSERT INTO user_features
SELECT 
    visitorid,

    COUNT(CASE WHEN event = 'view' THEN 1 END) AS view_count,
    COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS cart_count,
    COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS purchase_count,

    MAX(CASE WHEN event = 'view' THEN 1 ELSE 0 END) AS has_viewed,
    MAX(CASE WHEN event = 'addtocart' THEN 1 ELSE 0 END) AS has_carted,
    MAX(CASE WHEN event = 'transaction' THEN 1 ELSE 0 END) AS has_purchased,

    COUNT(CASE WHEN event = 'addtocart' THEN 1 END) * 1.0
        / NULLIF(COUNT(CASE WHEN event = 'view' THEN 1 END), 0) AS view_to_cart_rate,

    COUNT(CASE WHEN event = 'transaction' THEN 1 END) * 1.0
        / NULLIF(COUNT(CASE WHEN event = 'addtocart' THEN 1 END), 0) AS cart_to_purchase_rate,

    MAX(CASE WHEN event = 'transaction' THEN 1 ELSE 0 END) AS label_purchase
FROM events_raw
GROUP BY visitorid;

-- =========================
-- Export Sample for GitHub
-- =========================

-- Export a sample of user_features for demonstration (to avoid large file size)
-- Suggested: export ~10,000 rows as CSV via MySQL Workbench

SELECT *
FROM user_features
LIMIT 100;