USE ecommerce;

-- =========================
-- Funnel Analysis
-- =========================

-- 1. User counts at each stage
SELECT 
    COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END) AS view_users,
    COUNT(DISTINCT CASE WHEN event = 'addtocart' THEN visitorid END) AS cart_users,
    COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END) AS purchase_users
FROM events_raw;

-- 2. Conversion rates
SELECT 
    view_users,
    cart_users,
    purchase_users,
    cart_users * 1.0 / view_users AS view_to_cart_rate,
    purchase_users * 1.0 / cart_users AS cart_to_purchase_rate,
    purchase_users * 1.0 / view_users AS overall_conversion_rate
FROM (
    SELECT 
        COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END) AS view_users,
        COUNT(DISTINCT CASE WHEN event = 'addtocart' THEN visitorid END) AS cart_users,
        COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END) AS purchase_users
    FROM events_raw
) t;

  -- view to cart rate = 2.686%
  -- cart to purchase rate = 31.067%
  -- overall conversion rate (purchase/view) = 0.835%