-- ============================================================
-- STEP 1 — SETUP DATA
-- ============================================================

-- 1a. Load raw CSV into superstore_raw
--     
CREATE TABLE superstore_raw AS
    SELECT * FROM read_csv_auto('Sample_-_Superstore.csv');

-- 1b. Create normalized tables

CREATE TABLE customers AS
SELECT DISTINCT
    customer_id,
    customer_name,
    segment,
    city,
    state,
    region
FROM superstore_raw;

CREATE TABLE products AS
SELECT DISTINCT
    product_id,
    product_name,
    category,
    sub_category
FROM superstore_raw;

CREATE TABLE orders AS
SELECT DISTINCT
    order_id,
    customer_id,
    product_id,
    order_date,
    ship_date,
    ship_mode,
    sales,
    quantity,
    discount,
    profit
FROM superstore_raw;

-- Quick row count check
SELECT 'superstore_raw' AS tbl, COUNT(*) AS rows FROM superstore_raw UNION ALL
SELECT 'customers',             COUNT(*)           FROM customers      UNION ALL
SELECT 'products',              COUNT(*)           FROM products       UNION ALL
SELECT 'orders',                COUNT(*)           FROM orders;


-- ============================================================
-- STEP 2 — REQUIRED QUERIES
-- ============================================================

-- ── Q1: Orders where Sales > Average Sales (Subquery) ────────
SELECT
    order_id,
    customer_id,
    product_id,
    ROUND(sales, 2) AS sales
FROM orders
WHERE sales > (SELECT AVG(sales) FROM orders)
ORDER BY sales DESC;
-- Concept: scalar subquery in WHERE — computes one value (avg)
-- and compares every row against it.


-- ── Q2: Highest Sales Order Per Customer (Correlated Subquery) ──
SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    ROUND(o.sales, 2) AS sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.sales = (
    SELECT MAX(o2.sales)
    FROM orders o2
    WHERE o2.customer_id = o.customer_id   -- correlated: runs per row
)
ORDER BY o.sales DESC;
-- Concept: correlated subquery — re-runs for each outer row,
-- finding that customer's personal max.


-- ── Q3: Total Sales Per Customer (CTE) ──────────────────────
WITH customer_sales AS (
    SELECT
        o.customer_id,
        c.customer_name,
        ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name
)
SELECT * FROM customer_sales
ORDER BY total_sales DESC;
-- Concept: CTE (WITH clause) — like a named temp table,
-- makes complex queries readable and reusable.


-- ── Q4: Customers with Above-Average Total Sales (CTE + Subquery)
WITH customer_sales AS (
    SELECT
        o.customer_id,
        c.customer_name,
        ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name
)
SELECT *
FROM customer_sales
WHERE total_sales > (SELECT AVG(total_sales) FROM customer_sales)
ORDER BY total_sales DESC;
-- Concept: CTE referenced twice — once for data, once inside
-- a subquery for the average. Cleaner than nested subqueries.


-- ── Q5: Rank All Customers by Total Sales (Window Function — RANK)
WITH customer_sales AS (
    SELECT
        o.customer_id,
        c.customer_name,
        ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name
)
SELECT
    customer_id,
    customer_name,
    total_sales,
    RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
FROM customer_sales
ORDER BY sales_rank;
-- Concept: RANK() window function — assigns rank without
-- collapsing rows (unlike GROUP BY). Ties get the same rank.


-- ── Q6: Row Number Per Order Within Each Customer (ROW_NUMBER + PARTITION BY)
SELECT
    order_id,
    customer_id,
    ROUND(sales, 2) AS sales,
    order_date,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS order_row_num
FROM orders
ORDER BY customer_id, order_row_num;
-- Concept: PARTITION BY resets the counter for each customer.
-- ROW_NUMBER always gives unique sequential numbers (no ties).
-- Useful for "find the Nth order per customer" queries.


-- ── Q7: Top 3 Customers by Total Sales (Window Function) ─────
WITH customer_sales AS (
    SELECT
        o.customer_id,
        c.customer_name,
        ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name
),
ranked AS (
    SELECT *,
           RANK() OVER (ORDER BY total_sales DESC) AS rnk
    FROM customer_sales
)
SELECT customer_id, customer_name, total_sales, rnk
FROM ranked
WHERE rnk <= 3;
-- Concept: chain two CTEs — first aggregate, then rank,
-- then filter. Much more readable than nested subqueries.


-- ============================================================
-- STEP 3 — FINAL COMBINED QUERY
--          (JOIN + CTE + Window Function together)
-- ============================================================

WITH customer_sales AS (
    -- CTE: aggregate total sales per customer
    SELECT
        o.customer_id,
        ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    GROUP BY o.customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    cs.total_sales,
    RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id   -- JOIN for names
ORDER BY sales_rank;


-- ============================================================
-- MINI PROJECT — CUSTOMER SALES INSIGHTS
-- ============================================================

-- ── Q1: Top 5 Customers ──────────────────────────────────────
WITH cs AS (
    SELECT o.customer_id, c.customer_name,
           ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name
)
SELECT customer_name, total_sales,
       RANK() OVER (ORDER BY total_sales DESC) AS rnk
FROM cs
ORDER BY rnk
LIMIT 5;


-- ── Q2: Bottom 5 Customers ───────────────────────────────────
WITH cs AS (
    SELECT o.customer_id, c.customer_name,
           ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name
)
SELECT customer_name, total_sales,
       RANK() OVER (ORDER BY total_sales ASC) AS rnk
FROM cs
ORDER BY rnk
LIMIT 5;


-- ── Q3: Customers Who Made Only One Order ────────────────────
WITH order_counts AS (
    SELECT customer_id,
           COUNT(DISTINCT order_id) AS num_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    oc.num_orders
FROM order_counts oc
JOIN customers c ON oc.customer_id = c.customer_id
WHERE oc.num_orders = 1
ORDER BY c.customer_name;


-- ── Q4: Customers with Above-Average Total Sales ─────────────
WITH cs AS (
    SELECT o.customer_id, c.customer_name,
           ROUND(SUM(o.sales), 2) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.customer_name
)
SELECT customer_name, total_sales
FROM cs
WHERE total_sales > (SELECT AVG(total_sales) FROM cs)
ORDER BY total_sales DESC;


-- ── Q5: Highest Order Value Per Customer ─────────────────────
WITH ranked AS (
    SELECT
        o.order_id,
        c.customer_name,
        ROUND(o.sales, 2) AS sales,
        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY o.sales DESC
        ) AS rn
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
)
SELECT customer_name, order_id, sales AS highest_order_value
FROM ranked
WHERE rn = 1
ORDER BY highest_order_value DESC;
-- Uses ROW_NUMBER + PARTITION BY to grab only the #1 order
-- per customer instead of a correlated subquery.

-- ============================================================
-- END
-- ============================================================
