USE ecommerce;

-- =========================
-- Feature Engineering
-- =========================

DROP TABLE IF EXISTS user_features;

CREATE TABLE user_features AS
SELECT 
    visitorid,

    -- 行为计数
    COUNT(CASE WHEN event = 'view' THEN 1 END) AS view_count,
    COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS cart_count,
    COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS purchase_count,

    -- 行为强度（是否发生过）
    MAX(CASE WHEN event = 'view' THEN 1 ELSE 0 END) AS has_viewed,
    MAX(CASE WHEN event = 'addtocart' THEN 1 ELSE 0 END) AS has_carted,
    MAX(CASE WHEN event = 'transaction' THEN 1 ELSE 0 END) AS has_purchased,

    -- 转化率特征（非常关键）
    COUNT(CASE WHEN event = 'addtocart' THEN 1 END) * 1.0 
        / NULLIF(COUNT(CASE WHEN event = 'view' THEN 1 END), 0) AS view_to_cart_rate,

    COUNT(CASE WHEN event = 'transaction' THEN 1 END) * 1.0 
        / NULLIF(COUNT(CASE WHEN event = 'addtocart' THEN 1 END), 0) AS cart_to_purchase_rate,

    -- 标签（预测目标）
    MAX(CASE WHEN event = 'transaction' THEN 1 ELSE 0 END) AS label_purchase
FROM events_raw
GROUP BY visitorid;

-- Preview
SELECT * FROM user_features LIMIT 10;

-- Check label distribution
SELECT label_purchase, COUNT(*) 
FROM user_features
GROUP BY label_purchase;

-- =========================
-- Export Sample for GitHub
-- =========================

-- Export a sample of user_features for demonstration (to avoid large file size)
-- Suggested: export ~10,000 rows as CSV via MySQL Workbench

SELECT *
FROM user_features
LIMIT 10000;