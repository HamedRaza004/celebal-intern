import sqlite3
import os
from datetime import datetime, timedelta


DB_PATH = "data/ecommerce.db"


def get_test_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
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
            discount_percent REAL
        );
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            subcategory TEXT,
            cost_price REAL
        );
    """)
    return conn


def test_orphan_order_id():
    conn = get_test_conn()
    conn.execute("INSERT INTO orders VALUES ('O001','C001','2024-01-01 00:00:00','PLACED','NORTH')")
    conn.execute("INSERT INTO order_items VALUES ('I001','O999','P001',2,100.0,10.0)")
    conn.execute("INSERT INTO order_items VALUES ('I002','O001','P001',2,100.0,10.0)")

    rows = conn.execute("""
        SELECT oi.item_id FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
    """).fetchall()
    conn.close()

    orphans = [r["item_id"] for r in rows]
    passed = orphans == ["I001"]
    return {
        "test": "Orphan order_id in order_items",
        "passed": passed,
        "detail": f"Orphan items found: {orphans}" if orphans else "No orphans detected (unexpected)",
        "expected": "['I001']",
        "got": str(orphans),
    }


def test_discount_over_100():
    conn = get_test_conn()
    conn.execute("INSERT INTO orders VALUES ('O001','C001','2024-01-01 00:00:00','PLACED','NORTH')")
    conn.execute("INSERT INTO order_items VALUES ('I001','O001','P001',2,100.0,150.0)")
    conn.execute("INSERT INTO order_items VALUES ('I002','O001','P001',3,100.0,50.0)")

    rows = conn.execute("""
        SELECT item_id, discount_percent FROM order_items WHERE discount_percent > 100
    """).fetchall()
    conn.close()

    bad = [dict(r) for r in rows]
    passed = len(bad) == 1 and bad[0]["item_id"] == "I001"
    return {
        "test": "Discount percent > 100 detection",
        "passed": passed,
        "detail": f"Found {len(bad)} invalid discount(s): {bad}",
        "expected": "1 record with discount_percent=150.0",
        "got": str(bad),
    }


def test_zero_quantity():
    conn = get_test_conn()
    conn.execute("INSERT INTO orders VALUES ('O001','C001','2024-01-01 00:00:00','PLACED','NORTH')")
    conn.execute("INSERT INTO order_items VALUES ('I001','O001','P001',0,100.0,10.0)")
    conn.execute("INSERT INTO order_items VALUES ('I002','O001','P001',2,100.0,10.0)")

    rows = conn.execute("""
        SELECT item_id,
               quantity * unit_price * (1 - discount_percent / 100.0) AS revenue
        FROM order_items WHERE quantity = 0
    """).fetchall()
    conn.close()

    zero_rev = [dict(r) for r in rows]
    passed = len(zero_rev) == 1 and zero_rev[0]["revenue"] == 0.0
    return {
        "test": "Zero quantity revenue impact",
        "passed": passed,
        "detail": f"Zero-quantity items: {zero_rev}",
        "expected": "1 item with revenue=0.0",
        "got": str(zero_rev),
    }


def test_future_order_date():
    conn = get_test_conn()
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    past = "2024-01-01 10:00:00"
    conn.execute(f"INSERT INTO orders VALUES ('O001','C001','{future}','PLACED','NORTH')")
    conn.execute(f"INSERT INTO orders VALUES ('O002','C002','{past}','DELIVERED','SOUTH')")

    rows = conn.execute("""
        SELECT order_id, order_date FROM orders
        WHERE order_date > datetime('now')
    """).fetchall()
    conn.close()

    future_orders = [dict(r) for r in rows]
    passed = len(future_orders) == 1 and future_orders[0]["order_id"] == "O001"
    return {
        "test": "Future order_date detection",
        "passed": passed,
        "detail": f"Future-dated orders found: {[r['order_id'] for r in future_orders]}",
        "expected": "['O001']",
        "got": str([r["order_id"] for r in future_orders]),
    }


def run_all_tests():
    tests = [
        test_orphan_order_id,
        test_discount_over_100,
        test_zero_quantity,
        test_future_order_date,
    ]
    results = []
    for test_fn in tests:
        try:
            result = test_fn()
        except Exception as e:
            result = {
                "test": test_fn.__name__,
                "passed": False,
                "detail": f"Exception: {e}",
                "expected": "N/A",
                "got": "EXCEPTION",
            }
        results.append(result)
    return results


if __name__ == "__main__":
    results = run_all_tests()
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['test']}")
        print(f"       {r['detail']}")
