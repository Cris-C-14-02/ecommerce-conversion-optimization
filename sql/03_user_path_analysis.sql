USE ecommerce;

-- =========================
-- User Path Analysis
-- =========================

DROP VIEW IF EXISTS user_flags;

CREATE VIEW user_flags AS
SELECT 
    visitorid,
    MAX(CASE WHEN event = 'view' THEN 1 ELSE 0 END) AS viewed,
    MAX(CASE WHEN event = 'addtocart' THEN 1 ELSE 0 END) AS carted,
    MAX(CASE WHEN event = 'transaction' THEN 1 ELSE 0 END) AS purchased
FROM events_raw
GROUP BY visitorid;

-- Step 1: Preview user-level flags
SELECT *
FROM user_flags
LIMIT 10;

-- Step 2: Count user path distribution
SELECT 
    viewed,
    carted,
    purchased,
    COUNT(*) AS user_count
FROM user_flags
GROUP BY viewed, carted, purchased
ORDER BY user_count DESC;

-- Step 3: Count users who added to cart but did not purchase
SELECT COUNT(*) AS cart_not_purchase_users
FROM user_flags
WHERE carted = 1 AND purchased = 0;

-- =========================
-- User Path Analysis Result
-- =========================

-- viewed | carted | purchased | user_count
-- ----------------------------------------
--   1    |   0    |     0     | 1,368,715   → Only viewed (majority of users drop here)
--   1    |   1    |     0     |   24,173    → Added to cart but did not purchase (high-value target group)
--   1    |   1    |     1     |   10,228    → Successfully converted users
--   0    |   1    |     0     |    2,973    → Added to cart without recorded view (possible tracking anomaly)
--   1    |   0    |     1     |    1,063    → Purchased without cart (possible direct purchase behavior)
--   0    |   1    |     1     |      348    → Cart + purchase without view (rare / data noise)
--   0    |   0    |     1     |       80    → Purchase only (anomalous cases)

-- Key Insights:
-- 1. Majority of users (~1.37M) only browse without adding to cart → biggest drop-off occurs at view stage
-- 2. ~24K users added to cart but did not purchase → critical segment for marketing intervention
-- 3. Conversion from cart to purchase exists but still leaves optimization space
-- 4. Some abnormal paths exist (e.g., purchase without view), likely due to tracking limitations or data noise

-- Conclusion:
-- Focus should be on improving view-to-cart conversion and targeting cart-but-no-purchase users.