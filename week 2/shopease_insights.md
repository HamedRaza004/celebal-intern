# ShopEase — SQL Week 2 Task: Query Results & Insights

**Dataset:** 8 customers · 8 products · 10 orders · 15 order items

---

## Key Numbers at a Glance

| Metric | Value |
|---|---|
| Total Orders | 10 |
| Delivered Revenue | ₹17,191 |
| Avg product price | ₹2,149 |
| Products with discounts | 5 |

---

## Insights

**Orders by Status**

| Status | Orders | Revenue |
|---|---|---|
| Delivered | 6 | ₹17,191 |
| Shipped | 2 | ₹13,596 |
| Cancelled | 1 | ₹2,999 |
| Pending | 1 | ₹1,299 |

60% of orders are delivered. The 2 shipped orders (₹13,596) represent significant revenue still in transit.

---

**Avg Price by Category**

| Category | Avg Price |
|---|---|
| Clothing | ₹2,699 |
| Electronics | ₹2,224 |
| Home | ₹949 |

Clothing has the highest average price, driven by Nike Running Shoes (₹4,599). Home products are the most affordable category.

---

**Top Customers by Spend (Delivered orders)**

| Customer | Spent |
|---|---|
| Aarav Sharma | ₹7,997 |
| Vikram Singh | ₹5,898 |
| Divya Nair | ₹1,598 |

Aarav Sharma is the top spender with 2 delivered orders.

---

**Product Tier Breakdown**

| Tier | Products |
|---|---|
| Budget (<₹1000) | Cushion Covers, Cotton T-Shirt, Laptop Stand |
| Mid-Range (₹1000–3000) | Bedsheet Set, Wireless Earbuds, Smart Watch |
| Premium (>₹3000) | Bluetooth Speaker, Running Shoes |

---

**Delivered vs Not Delivered**

- Delivered: **6 orders**
- Not Delivered (Shipped/Pending/Cancelled): **4 orders**

---

## Constraint Highlights

- `email` → UNIQUE + NOT NULL: duplicate emails are rejected at DB level
- `unit_price` → CHECK > 0: negative prices blocked
- `customer_id` in orders → FK constraint: inserting `customer_id = 999` raises a foreign key violation error
- Wrapping inserts + stock updates in a `BEGIN…COMMIT` block ensures all steps succeed together or none do (Atomicity)

---

## Files

- `shopease_sql_week2.sql` — complete SQL script (schema + data + all queries)
