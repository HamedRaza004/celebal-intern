import csv
import random
import string
from datetime import datetime, timedelta

random.seed(42)

NUM_CUSTOMERS = 500
NUM_PRODUCTS = 200
NUM_ORDERS = 600
NUM_ITEMS = 900

REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]
STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Tablets", "Headphones", "Cameras"],
    "Clothing": ["Shirts", "Pants", "Dresses", "Shoes", "Accessories"],
    "Home": ["Furniture", "Kitchen", "Bedding", "Decor", "Lighting"],
    "Books": ["Fiction", "Non-Fiction", "Science", "History", "Technology"],
}

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Priya", "Ananya", "Isha", "Diya", "Riya", "Neha",
    "Pooja", "Shruti", "Kavya", "Megha", "James", "Oliver", "Harry", "Noah",
    "Emma", "Olivia", "Ava", "Isabella", "Sofia", "Charlotte",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Mehta", "Shah",
    "Joshi", "Nair", "Smith", "Johnson", "Williams", "Brown", "Jones",
    "Garcia", "Miller", "Davis", "Wilson", "Taylor",
]

PRODUCT_ADJECTIVES = ["Pro", "Elite", "Ultra", "Smart", "Premium", "Advanced", "Classic", "Deluxe"]
PRODUCT_NOUNS = {
    "Electronics": ["Phone", "Laptop", "Speaker", "Earbuds", "Watch", "Camera", "Tablet", "Monitor"],
    "Clothing": ["Shirt", "Jacket", "Dress", "Sneakers", "Hoodie", "Jeans", "Blazer", "Coat"],
    "Home": ["Chair", "Lamp", "Shelf", "Cushion", "Rug", "Curtain", "Vase", "Frame"],
    "Books": ["Guide", "Handbook", "Masterclass", "Journal", "Digest", "Collection", "Edition", "Volume"],
}

DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com"]


def random_date(start_year=2023, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def maybe_bad_date(dt, corrupt=False):
    if corrupt:
        return dt.strftime("%d-%m-%Y")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def generate_customers():
    customers = []
    used_emails = set()
    for i in range(1, NUM_CUSTOMERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        base_email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}"
        domain = random.choice(DOMAINS)
        email = f"{base_email}@{domain}"
        while email in used_emails:
            email = f"{base_email}{random.randint(1,9999)}@{domain}"
        used_emails.add(email)
        if random.random() < 0.02:
            bad = random.choice(["missing_at", "missing_domain"])
            if bad == "missing_at":
                email = f"{base_email}{domain}"
            else:
                email = f"{base_email}@"
        reg_date = random_date(2020, 2023).strftime("%Y-%m-%d")
        ctype = random.choice(CUSTOMER_TYPES)
        customers.append({
            "customer_id": f"C{i:04d}",
            "customer_name": name,
            "email": email,
            "registration_date": reg_date,
            "customer_type": ctype,
        })
    return customers


def generate_products():
    products = []
    used_names = set()
    for i in range(1, NUM_PRODUCTS + 1):
        cat = random.choice(list(CATEGORIES.keys()))
        subcat = random.choice(CATEGORIES[cat])
        adj = random.choice(PRODUCT_ADJECTIVES)
        noun = random.choice(PRODUCT_NOUNS[cat])
        brand_num = random.randint(100, 999)
        name = f"{adj} {noun} {brand_num}"
        while name.strip().lower() in used_names:
            name = f"{adj} {noun} {random.randint(100,9999)}"
        used_names.add(name.strip().lower())
        if random.random() < 0.08:
            mutations = [
                lambda n: "  " + n,
                lambda n: n + "  ",
                lambda n: n.upper(),
                lambda n: n.lower(),
                lambda n: n.replace(" ", "  "),
            ]
            name = random.choice(mutations)(name)
        cost = round(random.uniform(50, 5000), 2)
        products.append({
            "product_id": f"P{i:04d}",
            "product_name": name,
            "category": cat,
            "subcategory": subcat,
            "cost_price": cost,
        })
    return products


def generate_orders(customer_ids):
    orders = []
    for i in range(1, NUM_ORDERS + 1):
        order_date = random_date(2023, 2025)
        corrupt_date = random.random() < 0.05
        cid = random.choice(customer_ids)
        if random.random() < 0.05:
            cid = ""
        orders.append({
            "order_id": f"O{i:05d}",
            "customer_id": cid,
            "order_date": maybe_bad_date(order_date, corrupt_date),
            "status": random.choice(STATUSES),
            "region_code": random.choice(REGIONS),
        })
    return orders


def generate_order_items(order_ids, product_ids):
    items = []
    item_counter = 1
    for oid in order_ids:
        num_items = random.randint(1, 4)
        chosen_products = random.sample(product_ids, min(num_items, len(product_ids)))
        for pid in chosen_products:
            qty = random.randint(1, 10)
            if random.random() < 0.03:
                qty = -random.randint(1, 5)
            unit_price = round(random.uniform(100, 10000), 2)
            discount = round(random.uniform(0, 40), 2)
            items.append({
                "item_id": f"I{item_counter:06d}",
                "order_id": oid,
                "product_id": pid,
                "quantity": qty,
                "unit_price": unit_price,
                "discount_percent": discount,
            })
            item_counter += 1
    extra_needed = max(0, NUM_ITEMS - len(items))
    for _ in range(extra_needed):
        qty = random.randint(1, 10)
        if random.random() < 0.03:
            qty = -random.randint(1, 5)
        items.append({
            "item_id": f"I{item_counter:06d}",
            "order_id": random.choice(order_ids),
            "product_id": random.choice(product_ids),
            "quantity": qty,
            "unit_price": round(random.uniform(100, 10000), 2),
            "discount_percent": round(random.uniform(0, 40), 2),
        })
        item_counter += 1
    return items


def write_csv(filename, rows, fieldnames):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_all():
    customers = generate_customers()
    products = generate_products()
    customer_ids = [c["customer_id"] for c in customers]
    orders = generate_orders(customer_ids)
    order_ids = [o["order_id"] for o in orders]
    product_ids = [p["product_id"] for p in products]
    items = generate_order_items(order_ids, product_ids)

    write_csv("data/raw/customers.csv", customers,
              ["customer_id", "customer_name", "email", "registration_date", "customer_type"])
    write_csv("data/raw/products.csv", products,
              ["product_id", "product_name", "category", "subcategory", "cost_price"])
    write_csv("data/raw/orders.csv", orders,
              ["order_id", "customer_id", "order_date", "status", "region_code"])
    write_csv("data/raw/order_items.csv", items,
              ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])

    return len(customers), len(products), len(orders), len(items)


if __name__ == "__main__":
    import os
    os.makedirs("data/raw", exist_ok=True)
    c, p, o, i = generate_all()
    print(f"Generated: {c} customers, {p} products, {o} orders, {i} items")
