import sqlite3
from datetime import datetime, timedelta


DB_PATH = "data/ecommerce.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_date_range(report_type, start_date, end_date):
    if report_type == "daily":
        prev_start = start_date - timedelta(days=1)
        prev_end = end_date - timedelta(days=1)
    elif report_type == "weekly":
        prev_start = start_date - timedelta(weeks=1)
        prev_end = end_date - timedelta(weeks=1)
    else:
        prev_start = (start_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        prev_end = start_date.replace(day=1) - timedelta(days=1)
    return prev_start, prev_end


def fetch_period_stats(conn, start_str, end_str):
    row = conn.execute("""
        SELECT COUNT(DISTINCT o.order_id) AS total_orders,
               COUNT(DISTINCT o.customer_id) AS unique_customers,
               ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE oi.quantity > 0
          AND o.order_date >= ? AND o.order_date <= ?
          AND o.order_date != ''
    """, (start_str, end_str)).fetchone()
    return dict(row) if row else {"total_orders": 0, "unique_customers": 0, "revenue": 0}


def fetch_top_products(conn, start_str, end_str, limit=3):
    rows = conn.execute("""
        SELECT p.product_name,
               ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS revenue,
               SUM(oi.quantity) AS units_sold
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.quantity > 0
          AND o.order_date >= ? AND o.order_date <= ?
          AND o.order_date != ''
        GROUP BY p.product_id
        ORDER BY revenue DESC
        LIMIT ?
    """, (start_str, end_str, limit)).fetchall()
    return [dict(r) for r in rows]


def generate_report(report_type, start_date, end_date):
    conn = get_connection()

    start_str = start_date.strftime("%Y-%m-%d 00:00:00")
    end_str = end_date.strftime("%Y-%m-%d 23:59:59")

    current = fetch_period_stats(conn, start_str, end_str)
    top_products = fetch_top_products(conn, start_str, end_str)

    prev_start, prev_end = get_date_range(report_type, start_date, end_date)
    prev_start_str = prev_start.strftime("%Y-%m-%d 00:00:00")
    prev_end_str = prev_end.strftime("%Y-%m-%d 23:59:59")
    previous = fetch_period_stats(conn, prev_start_str, prev_end_str)

    conn.close()

    def pct_change(curr, prev):
        if prev and prev != 0:
            return round(100.0 * (curr - prev) / prev, 2)
        return None

    comparison = {
        "orders_change_pct": pct_change(current["total_orders"], previous["total_orders"]),
        "revenue_change_pct": pct_change(current["revenue"] or 0, previous["revenue"] or 0),
        "customers_change_pct": pct_change(current["unique_customers"], previous["unique_customers"]),
    }

    return {
        "report_type": report_type,
        "period": {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")},
        "prev_period": {"start": prev_start.strftime("%Y-%m-%d"), "end": prev_end.strftime("%Y-%m-%d")},
        "current": current,
        "previous": previous,
        "comparison": comparison,
        "top_products": top_products,
    }
