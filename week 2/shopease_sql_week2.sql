-- ============================================================
--  ShopEase E-Commerce Database — CEI Week 2 SQL Task
--  Database: DuckDB / PostgreSQL / MySQL compatible
-- ============================================================

-- ============================================================
-- SECTION 0 — SCHEMA CREATION
-- ============================================================

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    first_name  VARCHAR(50)  NOT NULL,
    last_name   VARCHAR(50)  NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    city        VARCHAR(50)  NOT NULL,
    state       VARCHAR(50)  NOT NULL,
    join_date   DATE         NOT NULL,
    is_premium  BOOLEAN      DEFAULT FALSE
);

CREATE TABLE products (
    product_id   INT          PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category     VARCHAR(50)  NOT NULL,
    brand        VARCHAR(50)  NOT NULL,
    unit_price   DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    stock_qty    INT           NOT NULL DEFAULT 0 CHECK (stock_qty >= 0)
);

CREATE TABLE orders (
    order_id     INT           PRIMARY KEY,
    customer_id  INT           NOT NULL,
    order_date   DATE          NOT NULL,
    status       VARCHAR(20)   NOT NULL DEFAULT 'Pending'
                 CHECK (status IN ('Pending','Shipped','Delivered','Cancelled')),
    total_amount DECIMAL(12,2) NOT NULL CHECK (total_amount >= 0),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id      INT           PRIMARY KEY,
    order_id     INT           NOT NULL,
    product_id   INT           NOT NULL,
    quantity     INT           NOT NULL CHECK (quantity > 0),
    unit_price   DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    discount_pct DECIMAL(5,2)  DEFAULT 0 CHECK (discount_pct BETWEEN 0 AND 100),
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes
CREATE INDEX idx_customers_city     ON customers(city);
CREATE INDEX idx_customers_state    ON customers(state);
CREATE INDEX idx_products_category  ON products(category);
CREATE INDEX idx_orders_date        ON orders(order_date);
CREATE INDEX idx_orders_status      ON orders(status);


-- ============================================================
-- SECTION 1 — SAMPLE DATA LOAD
-- ============================================================

INSERT INTO customers VALUES
(101,'Aarav','Sharma','aarav.s@email.com','Mumbai','Maharashtra','2024-01-15',TRUE),
(102,'Priya','Patel','priya.p@email.com','Ahmedabad','Gujarat','2024-02-20',FALSE),
(103,'Rohan','Gupta','rohan.g@email.com','Delhi','Delhi','2024-03-10',TRUE),
(104,'Sneha','Reddy','sneha.r@email.com','Hyderabad','Telangana','2024-04-05',FALSE),
(105,'Vikram','Singh','vikram.s@email.com','Jaipur','Rajasthan','2024-05-12',TRUE),
(106,'Ananya','Iyer','ananya.i@email.com','Chennai','Tamil Nadu','2024-06-18',FALSE),
(107,'Karan','Mehta','karan.m@email.com','Pune','Maharashtra','2024-07-22',TRUE),
(108,'Divya','Nair','divya.n@email.com','Kochi','Kerala','2024-08-30',FALSE);

INSERT INTO products VALUES
(201,'Wireless Earbuds','Electronics','BoAt',1499.00,250),
(202,'Cotton T-Shirt','Clothing','Levis',799.00,500),
(203,'Smart Watch','Electronics','Noise',2999.00,150),
(204,'Running Shoes','Clothing','Nike',4599.00,120),
(205,'Bluetooth Speaker','Electronics','JBL',3499.00,200),
(206,'Bedsheet Set','Home','Spaces',1299.00,300),
(207,'Laptop Stand','Electronics','AmazonBasics',899.00,180),
(208,'Cushion Covers (Set)','Home','HomeCenter',599.00,400);

INSERT INTO orders VALUES
(1001,101,'2024-08-01','Delivered',4498.00),
(1002,102,'2024-08-03','Delivered',799.00),
(1003,103,'2024-08-05','Shipped',7498.00),
(1004,101,'2024-08-10','Delivered',3499.00),
(1005,104,'2024-08-12','Cancelled',2999.00),
(1006,105,'2024-08-15','Delivered',5898.00),
(1007,106,'2024-08-18','Pending',1299.00),
(1008,103,'2024-08-20','Delivered',899.00),
(1009,107,'2024-08-25','Shipped',6098.00),
(1010,108,'2024-08-28','Delivered',1598.00);

INSERT INTO order_items VALUES
(5001,1001,201,2,1499.00,0),(5002,1001,207,1,899.00,10),
(5003,1002,202,1,799.00,0),(5004,1003,203,1,2999.00,0),
(5005,1003,204,1,4599.00,5),(5006,1004,205,1,3499.00,0),
(5007,1005,203,1,2999.00,0),(5008,1006,201,1,1499.00,10),
(5009,1006,204,1,4599.00,5),(5010,1007,206,1,1299.00,0),
(5011,1008,207,1,899.00,0),(5012,1009,205,1,3499.00,0),
(5013,1009,208,2,599.00,15),(5014,1010,206,1,1299.00,0),
(5015,1010,208,1,599.00,0);


-- ============================================================
-- SECTION 2 — SCHEMA EXPLORATION
-- ============================================================

-- All customers
SELECT * FROM customers;

-- All products
SELECT * FROM products;

-- Row counts per table
SELECT 'customers'  AS tbl, COUNT(*) AS rows FROM customers UNION ALL
SELECT 'products',          COUNT(*)          FROM products  UNION ALL
SELECT 'orders',            COUNT(*)          FROM orders    UNION ALL
SELECT 'order_items',       COUNT(*)          FROM order_items;

-- Unique categories
SELECT DISTINCT category FROM products ORDER BY category;

-- Data quality check — any NULLs in key columns?
SELECT
    SUM(CASE WHEN customer_id  IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN email        IS NULL THEN 1 ELSE 0 END) AS null_email,
    SUM(CASE WHEN city         IS NULL THEN 1 ELSE 0 END) AS null_city
FROM customers;


-- ============================================================
-- SECTION 3 — WHERE FILTERS
-- ============================================================

-- Q7: Delivered orders
SELECT * FROM orders WHERE status = 'Delivered';

-- Q8: Electronics above ₹2000
SELECT product_name, brand, unit_price
FROM products
WHERE category = 'Electronics' AND unit_price > 2000;

-- Q9: Maharashtra customers who joined in 2024
SELECT first_name, last_name, city, join_date
FROM customers
WHERE state = 'Maharashtra'
  AND join_date BETWEEN '2024-01-01' AND '2024-12-31';

-- Q10: Orders between Aug 10–25 (not cancelled)
SELECT order_id, order_date, status, total_amount
FROM orders
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25'
  AND status <> 'Cancelled';

-- Q12: SARGable version — index-friendly date filter
-- BAD  (breaks index): SELECT * FROM customers WHERE YEAR(join_date) = 2024;
-- GOOD (SARGable):
SELECT * FROM customers
WHERE join_date >= '2024-01-01'
  AND join_date <  '2025-01-01';


-- ============================================================
-- SECTION 4 — AGGREGATIONS (GROUP BY, SUM, COUNT, AVG, MIN, MAX)
-- ============================================================

-- Q13: Total orders
SELECT COUNT(*) AS total_orders FROM orders;

-- Q14: Total revenue from Delivered orders
SELECT SUM(total_amount) AS delivered_revenue
FROM orders
WHERE status = 'Delivered';

-- Q15: Average unit price per category
SELECT category,
       ROUND(AVG(unit_price), 2) AS avg_unit_price
FROM products
GROUP BY category
ORDER BY avg_unit_price DESC;

-- Q16: Order count + revenue per status, sorted by revenue desc
SELECT status,
       COUNT(*)           AS order_count,
       SUM(total_amount)  AS total_revenue
FROM orders
GROUP BY status
ORDER BY total_revenue DESC;

-- Q17: Most & least expensive product per category
SELECT category,
       MAX(unit_price) AS max_price,
       MIN(unit_price) AS min_price
FROM products
GROUP BY category;

-- Q18: Categories where avg price > ₹2000 (HAVING)
SELECT category,
       ROUND(AVG(unit_price), 2) AS avg_price
FROM products
GROUP BY category
HAVING AVG(unit_price) > 2000;


-- ============================================================
-- SECTION 5 — SORTING & TOP-N
-- ============================================================

-- Top 5 products by unit price
SELECT product_name, category, unit_price
FROM products
ORDER BY unit_price DESC
LIMIT 5;

-- Top customers by total spend (Delivered only)
SELECT c.first_name || ' ' || c.last_name AS customer,
       SUM(o.total_amount)                AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC;

-- Top categories by number of items sold
SELECT p.category,
       SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY units_sold DESC;


-- ============================================================
-- SECTION 6 — JOINS & RELATIONSHIPS
-- ============================================================

-- Q19: INNER JOIN — order + customer name
SELECT o.order_id, o.order_date,
       c.first_name, c.last_name,
       o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
ORDER BY o.order_date;

-- Q20: LEFT JOIN — all customers, even those with no orders
SELECT c.customer_id, c.first_name, c.last_name,
       o.order_id, o.order_date, o.status
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id;

-- Q21: 3-table join — order items with product details
SELECT o.order_id,
       p.product_name,
       oi.quantity,
       oi.unit_price,
       oi.discount_pct
FROM orders o
JOIN order_items oi ON o.order_id   = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
ORDER BY o.order_id;


-- ============================================================
-- SECTION 7 — USE CASES & BUSINESS QUERIES
-- ============================================================

-- Monthly sales trend (all orders)
SELECT EXTRACT(MONTH FROM order_date) AS month,
       COUNT(*)                        AS orders,
       SUM(total_amount)               AS revenue
FROM orders
GROUP BY month
ORDER BY month;

-- Customer lifetime value (CLV) — total spend per customer
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer,
       c.is_premium,
       COUNT(o.order_id)    AS total_orders,
       SUM(o.total_amount)  AS lifetime_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.is_premium
ORDER BY lifetime_value DESC NULLS LAST;

-- Revenue per product (actual sales amount after discount)
SELECT p.product_name,
       p.category,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)) AS net_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY net_revenue DESC;

-- Duplicate email check (data quality)
SELECT email, COUNT(*) AS cnt
FROM customers
GROUP BY email
HAVING COUNT(*) > 1;


-- ============================================================
-- SECTION 8 — CASE & CONDITIONAL LOGIC
-- ============================================================

-- Q24: Product price tier classification
SELECT product_name,
       unit_price,
       CASE
           WHEN unit_price < 1000              THEN 'Budget'
           WHEN unit_price BETWEEN 1000 AND 3000 THEN 'Mid-Range'
           ELSE                                     'Premium'
       END AS price_tier
FROM products
ORDER BY unit_price;

-- Q25: Delivered vs Not Delivered in one row
SELECT
    SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_count,
    SUM(CASE WHEN status <> 'Delivered' THEN 1 ELSE 0 END) AS not_delivered_count
FROM orders;

-- Premium vs non-premium revenue comparison
SELECT
    CASE WHEN c.is_premium THEN 'Premium' ELSE 'Standard' END AS customer_type,
    COUNT(DISTINCT o.order_id)  AS orders,
    SUM(o.total_amount)         AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.is_premium;


-- ============================================================
-- SECTION 9 — TRANSACTION (ACID EXAMPLE)
-- ============================================================

-- Q27: Atomic insert of new order + items + stock update
-- (PostgreSQL syntax; replace BEGIN with START TRANSACTION in MySQL)

BEGIN;

    -- Step 1: Insert the new order
    INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
    VALUES (1011, 102, CURRENT_DATE, 'Pending', 1598.00);

    -- Step 2: Insert order items
    INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
    VALUES (5016, 1011, 206, 1, 1299.00, 0);

    INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
    VALUES (5017, 1011, 208, 1, 599.00, 0);

    -- Step 3: Decrement stock for purchased products
    UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 206;
    UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 208;

COMMIT;
-- If anything above fails, run: ROLLBACK;


-- ============================================================
-- SECTION 10 — VALIDATION
-- ============================================================

-- Row counts sanity check
SELECT 'customers'  AS tbl, COUNT(*) AS rows FROM customers UNION ALL
SELECT 'products',          COUNT(*)          FROM products  UNION ALL
SELECT 'orders',            COUNT(*)          FROM orders    UNION ALL
SELECT 'order_items',       COUNT(*)          FROM order_items;

-- Check: no order_items with invalid order_id or product_id
SELECT COUNT(*) AS orphan_items
FROM order_items oi
WHERE NOT EXISTS (SELECT 1 FROM orders  o WHERE o.order_id   = oi.order_id)
   OR NOT EXISTS (SELECT 1 FROM products p WHERE p.product_id = oi.product_id);

-- Check: total_amount vs sum of item amounts (consistency check)
SELECT o.order_id,
       o.total_amount AS recorded_total,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS calculated_total
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.total_amount
ORDER BY o.order_id;
