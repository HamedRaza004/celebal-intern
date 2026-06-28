import csv
import re
import os
from datetime import datetime


def read_csv(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(filepath, rows, fieldnames):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_date(date_str):
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def clean_orders(input_path="data/raw/orders.csv", output_path="data/clean/orders.csv"):
    rows = read_csv(input_path)
    issues = []
    cleaned = []
    null_count = 0
    date_fixed = 0
    date_failed = 0

    for row in rows:
        original_date = row["order_date"]
        parsed = parse_date(original_date)
        if parsed is None:
            issues.append(f"[orders] Unparseable date '{original_date}' for order {row['order_id']}")
            date_failed += 1
            row["order_date"] = ""
        else:
            normalized = parsed.strftime("%Y-%m-%d %H:%M:%S")
            if normalized != original_date.strip():
                date_fixed += 1
            row["order_date"] = normalized

        if not row["customer_id"].strip():
            issues.append(f"[orders] NULL customer_id for order {row['order_id']}")
            null_count += 1
            row["customer_id"] = "UNKNOWN"

        cleaned.append(row)

    write_csv(output_path, cleaned, ["order_id", "customer_id", "order_date", "status", "region_code"])
    return cleaned, issues, {
        "total": len(rows),
        "null_customer_ids": null_count,
        "dates_fixed": date_fixed,
        "dates_failed": date_failed,
    }


def clean_products(input_path="data/raw/products.csv", output_path="data/clean/products.csv"):
    rows = read_csv(input_path)
    issues = []
    cleaned = []
    normalized_count = 0

    for row in rows:
        original = row["product_name"]
        fixed = original.strip().title()
        while "  " in fixed:
            fixed = fixed.replace("  ", " ")
        if fixed != original:
            issues.append(f"[products] Normalized name '{original.strip()}' -> '{fixed}' for {row['product_id']}")
            normalized_count += 1
        row["product_name"] = fixed
        cleaned.append(row)

    write_csv(output_path, cleaned, ["product_id", "product_name", "category", "subcategory", "cost_price"])
    return cleaned, issues, {"total": len(rows), "names_normalized": normalized_count}


def validate_emails(input_path="data/raw/customers.csv", output_path="data/clean/customers.csv"):
    rows = read_csv(input_path)
    invalid_ids = []
    issues = []
    cleaned = []
    email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    for row in rows:
        email = row["email"]
        if not email_pattern.match(email):
            invalid_ids.append(row["customer_id"])
            issues.append(f"[customers] Invalid email '{email}' for customer {row['customer_id']}")
            row["email_valid"] = "NO"
        else:
            row["email_valid"] = "YES"
        cleaned.append(row)

    write_csv(output_path, cleaned,
              ["customer_id", "customer_name", "email", "email_valid", "registration_date", "customer_type"])
    return invalid_ids, issues, {"total": len(rows), "invalid_emails": len(invalid_ids)}


def check_referential_integrity(
    orders_path="data/raw/orders.csv",
    items_path="data/raw/order_items.csv",
    output_path="data/clean/order_items.csv",
):
    orders = read_csv(orders_path)
    items = read_csv(items_path)
    valid_order_ids = {o["order_id"] for o in orders}
    orphan_items = []
    valid_items = []
    issues = []

    for item in items:
        if item["order_id"] not in valid_order_ids:
            orphan_items.append(item["item_id"])
            issues.append(
                f"[order_items] Orphan item {item['item_id']} references non-existent order {item['order_id']}"
            )
        else:
            valid_items.append(item)

    write_csv(output_path, valid_items,
              ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])
    return orphan_items, issues, {
        "total_items": len(items),
        "orphan_items": len(orphan_items),
        "valid_items": len(valid_items),
    }


def run_all_cleaning():
    os.makedirs("data/clean", exist_ok=True)
    all_issues = []
    stats = {}

    _, order_issues, order_stats = clean_orders()
    all_issues.extend(order_issues)
    stats["orders"] = order_stats

    _, product_issues, product_stats = clean_products()
    all_issues.extend(product_issues)
    stats["products"] = product_stats

    _, customer_issues, customer_stats = validate_emails()
    all_issues.extend(customer_issues)
    stats["customers"] = customer_stats

    _, integrity_issues, integrity_stats = check_referential_integrity()
    all_issues.extend(integrity_issues)
    stats["order_items"] = integrity_stats

    report_path = "data/cleaning_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("DATA CLEANING REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("STATISTICS\n")
        f.write("-" * 40 + "\n")
        for section, s in stats.items():
            f.write(f"\n[{section.upper()}]\n")
            for k, v in s.items():
                f.write(f"  {k}: {v}\n")
        f.write("\n\nISSUES FOUND\n")
        f.write("-" * 40 + "\n")
        if all_issues:
            for issue in all_issues:
                f.write(f"  {issue}\n")
        else:
            f.write("  No issues found.\n")

    return all_issues, stats, report_path


if __name__ == "__main__":
    issues, stats, report = run_all_cleaning()
    print(f"Cleaning complete. {len(issues)} issues found. Report saved to {report}")
