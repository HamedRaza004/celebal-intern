import sqlite3
import csv
import os


DB_PATH = "data/ecommerce.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def load_data_to_db():
    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS products;

        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT,
            email TEXT,
            email_valid TEXT,
            registration_date TEXT,
            customer_type TEXT
        );

        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            subcategory TEXT,
            cost_price REAL
        );

        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            order_date TEXT,
            status TEXT,
            region_code TEXT
        );

        CREATE TABLE order_items (
            item_id TEXT PRIMARY KEY,
            order_id TEXT,
            product_id TEXT,
            quantity INTEGER,
            unit_price REAL,
            discount_percent REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """)

    def load_csv(path, table, fields):
        if not os.path.exists(path):
            return 0
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append(tuple(row.get(field, "") for field in fields))
        placeholders = ",".join(["?" for _ in fields])
        cols = ",".join(fields)
        c.executemany(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})", rows)
        return len(rows)

    customers_path = "data/clean/customers.csv" if os.path.exists("data/clean/customers.csv") else "data/raw/customers.csv"
    products_path = "data/clean/products.csv" if os.path.exists("data/clean/products.csv") else "data/raw/products.csv"
    orders_path = "data/clean/orders.csv" if os.path.exists("data/clean/orders.csv") else "data/raw/orders.csv"
    items_path = "data/clean/order_items.csv" if os.path.exists("data/clean/order_items.csv") else "data/raw/order_items.csv"

    n_customers = load_csv(customers_path, "customers",
                           ["customer_id", "customer_name", "email", "email_valid", "registration_date", "customer_type"])
    n_products = load_csv(products_path, "products",
                          ["product_id", "product_name", "category", "subcategory", "cost_price"])
    n_orders = load_csv(orders_path, "orders",
                        ["order_id", "customer_id", "order_date", "status", "region_code"])
    n_items = load_csv(items_path, "order_items",
                       ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])

    conn.commit()
    conn.close()
    return n_customers, n_products, n_orders, n_items


def q1_revenue_per_category():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.category,
               ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.quantity > 0
        GROUP BY p.category
        ORDER BY total_revenue DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q2_top10_customers():
    conn = get_connection()
    rows = conn.execute("""
        SELECT o.customer_id,
               c.customer_name,
               ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_value
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE oi.quantity > 0
        GROUP BY o.customer_id
        ORDER BY total_value DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q3_monthly_order_count():
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', order_date) AS month,
               COUNT(*) AS order_count
        FROM orders
        WHERE order_date >= date('now', '-12 months')
          AND order_date != ''
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q4_customers_never_delivered():
    conn = get_connection()
    rows = conn.execute("""
        SELECT DISTINCT o.customer_id, c.customer_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.customer_id NOT IN (
            SELECT DISTINCT customer_id FROM orders WHERE status = 'DELIVERED'
        )
        AND o.customer_id != 'UNKNOWN'
        ORDER BY o.customer_id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q5_more_returns_than_purchases():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.product_id, p.product_name,
               SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS purchases,
               ABS(SUM(CASE WHEN oi.quantity < 0 THEN oi.quantity ELSE 0 END)) AS returns
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id
        HAVING returns > purchases
        ORDER BY returns DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q6_return_rate_per_category():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.category,
               SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) AS returned_items,
               SUM(ABS(oi.quantity)) AS total_items,
               ROUND(
                   100.0 * SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) /
                   NULLIF(SUM(ABS(oi.quantity)), 0), 2
               ) AS return_rate_pct
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY return_rate_pct DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q7_running_totals():
    conn = get_connection()
    rows = conn.execute("""
        WITH daily AS (
            SELECT o.region_code,
                   DATE(o.order_date) AS order_date,
                   ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS daily_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0 AND o.order_date != ''
            GROUP BY o.region_code, DATE(o.order_date)
        )
        SELECT region_code, order_date, daily_revenue,
               ROUND(SUM(daily_revenue) OVER (
                   PARTITION BY region_code ORDER BY order_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
               ), 2) AS running_total
        FROM daily
        ORDER BY region_code, order_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q8_product_ranking_by_category():
    conn = get_connection()
    rows = conn.execute("""
        WITH rev AS (
            SELECT p.category, p.product_name,
                   ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.quantity > 0
            GROUP BY p.category, p.product_name
        )
        SELECT category, product_name, total_revenue,
               DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
        FROM rev
        ORDER BY category, rank_in_category
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q9_lag_lead_analysis():
    conn = get_connection()
    rows = conn.execute("""
        WITH ordered AS (
            SELECT customer_id, order_date,
                   LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
            FROM orders
            WHERE order_date != '' AND customer_id != 'UNKNOWN'
        ),
        with_gap AS (
            SELECT customer_id, order_date, previous_order_date,
                   CASE WHEN previous_order_date IS NOT NULL
                        THEN CAST(julianday(order_date) - julianday(previous_order_date) AS INTEGER)
                        ELSE NULL
                   END AS days_gap
            FROM ordered
        ),
        avg_gap AS (
            SELECT customer_id, AVG(days_gap) AS avg_days_gap
            FROM with_gap
            WHERE days_gap IS NOT NULL
            GROUP BY customer_id
        )
        SELECT wg.customer_id, wg.order_date, wg.previous_order_date, wg.days_gap,
               CASE WHEN ag.avg_days_gap > 30 THEN 'At Risk' ELSE 'Active' END AS risk_flag
        FROM with_gap wg
        LEFT JOIN avg_gap ag ON wg.customer_id = ag.customer_id
        ORDER BY wg.customer_id, wg.order_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q10_cte_multilevel():
    conn = get_connection()
    rows = conn.execute("""
        WITH monthly_revenue AS (
            SELECT o.customer_id,
                   strftime('%Y-%m', o.order_date) AS month,
                   SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0 AND o.order_date != ''
            GROUP BY o.customer_id, month
        ),
        categorized AS (
            SELECT month, customer_id, revenue,
                   CASE WHEN revenue > 10000 THEN 'High'
                        WHEN revenue >= 5000 THEN 'Medium'
                        ELSE 'Low' END AS revenue_category
            FROM monthly_revenue
        )
        SELECT month, revenue_category, COUNT(customer_id) AS customer_count
        FROM categorized
        GROUP BY month, revenue_category
        ORDER BY month DESC, revenue_category
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q11_ntile_segmentation():
    conn = get_connection()
    rows = conn.execute("""
        WITH lifetime AS (
            SELECT o.customer_id,
                   ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_value
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0
            GROUP BY o.customer_id
        )
        SELECT customer_id, total_value,
               NTILE(4) OVER (ORDER BY total_value DESC) AS quartile,
               CASE NTILE(4) OVER (ORDER BY total_value DESC)
                   WHEN 1 THEN 'Platinum'
                   WHEN 2 THEN 'Gold'
                   WHEN 3 THEN 'Silver'
                   WHEN 4 THEN 'Bronze'
               END AS quartile_label
        FROM lifetime
        ORDER BY total_value DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q12_yoy_comparison():
    conn = get_connection()
    rows = conn.execute("""
        WITH monthly AS (
            SELECT strftime('%Y', o.order_date) AS year,
                   strftime('%m', o.order_date) AS month,
                   ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0 AND o.order_date != ''
            GROUP BY year, month
        )
        SELECT curr.year, curr.month, curr.revenue,
               prev.revenue AS prev_year_revenue,
               CASE WHEN prev.revenue IS NOT NULL AND prev.revenue != 0
                    THEN ROUND(100.0 * (curr.revenue - prev.revenue) / prev.revenue, 2)
                    ELSE NULL
               END AS yoy_growth_percent
        FROM monthly curr
        LEFT JOIN monthly prev ON curr.month = prev.month AND CAST(curr.year AS INTEGER) = CAST(prev.year AS INTEGER) + 1
        ORDER BY curr.year DESC, curr.month DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q13_first_last_category():
    conn = get_connection()
    rows = conn.execute("""
        WITH ordered_purchases AS (
            SELECT o.customer_id, p.category,
                   ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC) AS rn_first,
                   ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC) AS rn_last
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.order_date != ''
        )
        SELECT f.customer_id,
               f.category AS first_category,
               l.category AS last_category,
               CASE WHEN f.category != l.category THEN 'Yes' ELSE 'No' END AS category_shift
        FROM (SELECT customer_id, category FROM ordered_purchases WHERE rn_first = 1) f
        JOIN (SELECT customer_id, category FROM ordered_purchases WHERE rn_last = 1) l
          ON f.customer_id = l.customer_id
        ORDER BY category_shift DESC, f.customer_id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q14_cumulative_distribution():
    conn = get_connection()
    rows = conn.execute("""
        WITH customer_revenue AS (
            SELECT o.customer_id,
                   ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0
            GROUP BY o.customer_id
        ),
        total AS (SELECT SUM(revenue) AS grand_total FROM customer_revenue)
        SELECT cr.customer_id, cr.revenue,
               ROUND(SUM(cr.revenue) OVER (ORDER BY cr.revenue DESC
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_revenue,
               ROUND(100.0 * SUM(cr.revenue) OVER (ORDER BY cr.revenue DESC
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / t.grand_total, 2) AS cumulative_percent
        FROM customer_revenue cr, total t
        ORDER BY cr.revenue DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q15_cohort_analysis():
    conn = get_connection()
    rows = conn.execute("""
        WITH cohort_base AS (
            SELECT c.customer_id,
                   strftime('%Y-%m', c.registration_date) AS cohort_month
            FROM customers c
        ),
        customer_orders AS (
            SELECT o.customer_id,
                   strftime('%Y-%m', o.order_date) AS order_month
            FROM orders o
            WHERE o.order_date != '' AND o.customer_id != 'UNKNOWN'
        ),
        cohort_orders AS (
            SELECT cb.cohort_month, co.customer_id, co.order_month,
                   (CAST(strftime('%Y', co.order_month || '-01') AS INTEGER) * 12 +
                    CAST(strftime('%m', co.order_month || '-01') AS INTEGER)) -
                   (CAST(strftime('%Y', cb.cohort_month || '-01') AS INTEGER) * 12 +
                    CAST(strftime('%m', cb.cohort_month || '-01') AS INTEGER)) AS months_since_join
            FROM cohort_base cb
            JOIN customer_orders co ON cb.customer_id = co.customer_id
        ),
        cohort_size AS (
            SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_total
            FROM cohort_base
            GROUP BY cohort_month
        )
        SELECT co.cohort_month,
               cs.cohort_total,
               co.months_since_join,
               COUNT(DISTINCT co.customer_id) AS active_customers,
               ROUND(100.0 * COUNT(DISTINCT co.customer_id) / cs.cohort_total, 2) AS retention_rate
        FROM cohort_orders co
        JOIN cohort_size cs ON co.cohort_month = cs.cohort_month
        WHERE co.months_since_join BETWEEN 0 AND 3
        GROUP BY co.cohort_month, co.months_since_join
        ORDER BY co.cohort_month, co.months_since_join
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q16_products_bought_together():
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.product_id AS product_a_id, pa.product_name AS product_a,
               b.product_id AS product_b_id, pb.product_name AS product_b,
               COUNT(*) AS times_bought_together
        FROM order_items a
        JOIN order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
        JOIN products pa ON a.product_id = pa.product_id
        JOIN products pb ON b.product_id = pb.product_id
        GROUP BY a.product_id, b.product_id
        ORDER BY times_bought_together DESC
        LIMIT 20
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


ALL_QUERIES = {
    "q1": ("Total Revenue per Category", q1_revenue_per_category),
    "q2": ("Top 10 Customers by Order Value", q2_top10_customers),
    "q3": ("Month-wise Order Count (Last 12 Months)", q3_monthly_order_count),
    "q4": ("Customers Never Had Delivery", q4_customers_never_delivered),
    "q5": ("Products with More Returns than Purchases", q5_more_returns_than_purchases),
    "q6": ("Return Rate per Category", q6_return_rate_per_category),
    "q7": ("Running Totals by Region", q7_running_totals),
    "q8": ("Product Ranking by Category (DENSE_RANK)", q8_product_ranking_by_category),
    "q9": ("LAG/LEAD: Days Between Orders", q9_lag_lead_analysis),
    "q10": ("CTE Multi-level: Customer Revenue Categories", q10_cte_multilevel),
    "q11": ("NTILE: Customer Segmentation", q11_ntile_segmentation),
    "q12": ("Year-over-Year Revenue Comparison", q12_yoy_comparison),
    "q13": ("First vs Last Category (Category Shift)", q13_first_last_category),
    "q14": ("Cumulative Revenue Distribution", q14_cumulative_distribution),
    "q15": ("Cohort Retention Analysis", q15_cohort_analysis),
    "q16": ("Products Frequently Bought Together", q16_products_bought_together),
}
