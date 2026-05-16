# ShopEase E-Commerce — SQL Query Results

> **CEI Summer Internship 2026 | Week 2 Task**  
> Dataset: 8 customers · 8 products · 10 orders · 15 order items

---

## SECTION 2 — SCHEMA EXPLORATION

### All Customers

| customer_id | first_name | last_name | email | city | state | join_date | is_premium |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | Aarav | Sharma | aarav.s@email.com | Mumbai | Maharashtra | 2024-01-15 00:00:00 | True |
| 102 | Priya | Patel | priya.p@email.com | Ahmedabad | Gujarat | 2024-02-20 00:00:00 | False |
| 103 | Rohan | Gupta | rohan.g@email.com | Delhi | Delhi | 2024-03-10 00:00:00 | True |
| 104 | Sneha | Reddy | sneha.r@email.com | Hyderabad | Telangana | 2024-04-05 00:00:00 | False |
| 105 | Vikram | Singh | vikram.s@email.com | Jaipur | Rajasthan | 2024-05-12 00:00:00 | True |
| 106 | Ananya | Iyer | ananya.i@email.com | Chennai | Tamil Nadu | 2024-06-18 00:00:00 | False |
| 107 | Karan | Mehta | karan.m@email.com | Pune | Maharashtra | 2024-07-22 00:00:00 | True |
| 108 | Divya | Nair | divya.n@email.com | Kochi | Kerala | 2024-08-30 00:00:00 | False |

### All Products

| product_id | product_name | category | brand | unit_price | stock_qty |
| --- | --- | --- | --- | --- | --- |
| 201 | Wireless Earbuds | Electronics | BoAt | 1499.0 | 250 |
| 202 | Cotton T-Shirt | Clothing | Levis | 799.0 | 500 |
| 203 | Smart Watch | Electronics | Noise | 2999.0 | 150 |
| 204 | Running Shoes | Clothing | Nike | 4599.0 | 120 |
| 205 | Bluetooth Speaker | Electronics | JBL | 3499.0 | 200 |
| 206 | Bedsheet Set | Home | Spaces | 1299.0 | 300 |
| 207 | Laptop Stand | Electronics | AmazonBasics | 899.0 | 180 |
| 208 | Cushion Covers (Set) | Home | HomeCenter | 599.0 | 400 |

### All Orders

| order_id | customer_id | order_date | status | total_amount |
| --- | --- | --- | --- | --- |
| 1001 | 101 | 2024-08-01 00:00:00 | Delivered | 4498.0 |
| 1002 | 102 | 2024-08-03 00:00:00 | Delivered | 799.0 |
| 1003 | 103 | 2024-08-05 00:00:00 | Shipped | 7498.0 |
| 1004 | 101 | 2024-08-10 00:00:00 | Delivered | 3499.0 |
| 1005 | 104 | 2024-08-12 00:00:00 | Cancelled | 2999.0 |
| 1006 | 105 | 2024-08-15 00:00:00 | Delivered | 5898.0 |
| 1007 | 106 | 2024-08-18 00:00:00 | Pending | 1299.0 |
| 1008 | 103 | 2024-08-20 00:00:00 | Delivered | 899.0 |
| 1009 | 107 | 2024-08-25 00:00:00 | Shipped | 6098.0 |
| 1010 | 108 | 2024-08-28 00:00:00 | Delivered | 1598.0 |

### All Order Items

| item_id | order_id | product_id | quantity | unit_price | discount_pct |
| --- | --- | --- | --- | --- | --- |
| 5001.0 | 1001.0 | 201.0 | 2.0 | 1499.0 | 0.0 |
| 5002.0 | 1001.0 | 207.0 | 1.0 | 899.0 | 10.0 |
| 5003.0 | 1002.0 | 202.0 | 1.0 | 799.0 | 0.0 |
| 5004.0 | 1003.0 | 203.0 | 1.0 | 2999.0 | 0.0 |
| 5005.0 | 1003.0 | 204.0 | 1.0 | 4599.0 | 5.0 |
| 5006.0 | 1004.0 | 205.0 | 1.0 | 3499.0 | 0.0 |
| 5007.0 | 1005.0 | 203.0 | 1.0 | 2999.0 | 0.0 |
| 5008.0 | 1006.0 | 201.0 | 1.0 | 1499.0 | 10.0 |
| 5009.0 | 1006.0 | 204.0 | 1.0 | 4599.0 | 5.0 |
| 5010.0 | 1007.0 | 206.0 | 1.0 | 1299.0 | 0.0 |
| 5011.0 | 1008.0 | 207.0 | 1.0 | 899.0 | 0.0 |
| 5012.0 | 1009.0 | 205.0 | 1.0 | 3499.0 | 0.0 |
| 5013.0 | 1009.0 | 208.0 | 2.0 | 599.0 | 15.0 |
| 5014.0 | 1010.0 | 206.0 | 1.0 | 1299.0 | 0.0 |
| 5015.0 | 1010.0 | 208.0 | 1.0 | 599.0 | 0.0 |

### Row Counts Per Table

| table_name | row_count |
| --- | --- |
| customers | 8 |
| products | 8 |
| orders | 10 |
| order_items | 15 |

### Unique Categories

| category |
| --- |
| Clothing |
| Electronics |
| Home |

---

## SECTION 3 — WHERE FILTERS

### Q7: Delivered Orders

| order_id | customer_id | order_date | status | total_amount |
| --- | --- | --- | --- | --- |
| 1001 | 101 | 2024-08-01 00:00:00 | Delivered | 4498.0 |
| 1002 | 102 | 2024-08-03 00:00:00 | Delivered | 799.0 |
| 1004 | 101 | 2024-08-10 00:00:00 | Delivered | 3499.0 |
| 1006 | 105 | 2024-08-15 00:00:00 | Delivered | 5898.0 |
| 1008 | 103 | 2024-08-20 00:00:00 | Delivered | 899.0 |
| 1010 | 108 | 2024-08-28 00:00:00 | Delivered | 1598.0 |

### Q8: Electronics Above ₹2000

| product_name | brand | unit_price |
| --- | --- | --- |
| Smart Watch | Noise | 2999.0 |
| Bluetooth Speaker | JBL | 3499.0 |

### Q9: Maharashtra Customers (2024)

| first_name | last_name | city | join_date |
| --- | --- | --- | --- |
| Aarav | Sharma | Mumbai | 2024-01-15 00:00:00 |
| Karan | Mehta | Pune | 2024-07-22 00:00:00 |

### Q10: Orders Aug 10–25 Not Cancelled

| order_id | order_date | status | total_amount |
| --- | --- | --- | --- |
| 1004 | 2024-08-10 00:00:00 | Delivered | 3499.0 |
| 1006 | 2024-08-15 00:00:00 | Delivered | 5898.0 |
| 1007 | 2024-08-18 00:00:00 | Pending | 1299.0 |
| 1008 | 2024-08-20 00:00:00 | Delivered | 899.0 |
| 1009 | 2024-08-25 00:00:00 | Shipped | 6098.0 |

### Q12: SARGable Date Filter (index-friendly)

| customer_id | first_name | last_name | email | city | state | join_date | is_premium |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | Aarav | Sharma | aarav.s@email.com | Mumbai | Maharashtra | 2024-01-15 00:00:00 | True |
| 102 | Priya | Patel | priya.p@email.com | Ahmedabad | Gujarat | 2024-02-20 00:00:00 | False |
| 103 | Rohan | Gupta | rohan.g@email.com | Delhi | Delhi | 2024-03-10 00:00:00 | True |
| 104 | Sneha | Reddy | sneha.r@email.com | Hyderabad | Telangana | 2024-04-05 00:00:00 | False |
| 105 | Vikram | Singh | vikram.s@email.com | Jaipur | Rajasthan | 2024-05-12 00:00:00 | True |
| 106 | Ananya | Iyer | ananya.i@email.com | Chennai | Tamil Nadu | 2024-06-18 00:00:00 | False |
| 107 | Karan | Mehta | karan.m@email.com | Pune | Maharashtra | 2024-07-22 00:00:00 | True |
| 108 | Divya | Nair | divya.n@email.com | Kochi | Kerala | 2024-08-30 00:00:00 | False |

---

## SECTION 4 — AGGREGATIONS

### Q13: Total Number of Orders

| total_orders |
| --- |
| 10 |

### Q14: Total Revenue from Delivered Orders

| delivered_revenue |
| --- |
| 17191.0 |

### Q15: Avg Unit Price Per Category

| category | avg_unit_price |
| --- | --- |
| Clothing | 2699.0 |
| Electronics | 2224.0 |
| Home | 949.0 |

### Q16: Order Count & Revenue Per Status

| status | order_count | total_revenue |
| --- | --- | --- |
| Delivered | 6 | 17191.0 |
| Shipped | 2 | 13596.0 |
| Cancelled | 1 | 2999.0 |
| Pending | 1 | 1299.0 |

### Q17: Max & Min Price Per Category

| category | max_price | min_price |
| --- | --- | --- |
| Electronics | 3499.0 | 899.0 |
| Clothing | 4599.0 | 799.0 |
| Home | 1299.0 | 599.0 |

### Q18: Categories with Avg Price > ₹2000 (HAVING)

| category | avg_price |
| --- | --- |
| Electronics | 2224.0 |
| Clothing | 2699.0 |

---

## SECTION 5 — SORTING & TOP-N

### Top 5 Products by Unit Price

| product_name | category | unit_price |
| --- | --- | --- |
| Running Shoes | Clothing | 4599.0 |
| Bluetooth Speaker | Electronics | 3499.0 |
| Smart Watch | Electronics | 2999.0 |
| Wireless Earbuds | Electronics | 1499.0 |
| Bedsheet Set | Home | 1299.0 |

### Top Customers by Total Spend (Delivered)

| customer | total_spent |
| --- | --- |
| Aarav Sharma | 7997.0 |
| Vikram Singh | 5898.0 |
| Divya Nair | 1598.0 |
| Rohan Gupta | 899.0 |
| Priya Patel | 799.0 |

### Top Categories by Units Sold

| category | units_sold |
| --- | --- |
| Electronics | 9.0 |
| Home | 5.0 |
| Clothing | 3.0 |

---

## SECTION 6 — JOINS & RELATIONSHIPS

### Q19: INNER JOIN — Orders with Customer Names

| order_id | order_date | first_name | last_name | total_amount |
| --- | --- | --- | --- | --- |
| 1001 | 2024-08-01 00:00:00 | Aarav | Sharma | 4498.0 |
| 1002 | 2024-08-03 00:00:00 | Priya | Patel | 799.0 |
| 1003 | 2024-08-05 00:00:00 | Rohan | Gupta | 7498.0 |
| 1004 | 2024-08-10 00:00:00 | Aarav | Sharma | 3499.0 |
| 1005 | 2024-08-12 00:00:00 | Sneha | Reddy | 2999.0 |
| 1006 | 2024-08-15 00:00:00 | Vikram | Singh | 5898.0 |
| 1007 | 2024-08-18 00:00:00 | Ananya | Iyer | 1299.0 |
| 1008 | 2024-08-20 00:00:00 | Rohan | Gupta | 899.0 |
| 1009 | 2024-08-25 00:00:00 | Karan | Mehta | 6098.0 |
| 1010 | 2024-08-28 00:00:00 | Divya | Nair | 1598.0 |

### Q20: LEFT JOIN — All Customers + Orders (incl. no orders)

| customer_id | first_name | last_name | order_id | order_date | status |
| --- | --- | --- | --- | --- | --- |
| 101 | Aarav | Sharma | 1001 | 2024-08-01 00:00:00 | Delivered |
| 101 | Aarav | Sharma | 1004 | 2024-08-10 00:00:00 | Delivered |
| 102 | Priya | Patel | 1002 | 2024-08-03 00:00:00 | Delivered |
| 103 | Rohan | Gupta | 1003 | 2024-08-05 00:00:00 | Shipped |
| 103 | Rohan | Gupta | 1008 | 2024-08-20 00:00:00 | Delivered |
| 104 | Sneha | Reddy | 1005 | 2024-08-12 00:00:00 | Cancelled |
| 105 | Vikram | Singh | 1006 | 2024-08-15 00:00:00 | Delivered |
| 106 | Ananya | Iyer | 1007 | 2024-08-18 00:00:00 | Pending |
| 107 | Karan | Mehta | 1009 | 2024-08-25 00:00:00 | Shipped |
| 108 | Divya | Nair | 1010 | 2024-08-28 00:00:00 | Delivered |

### Q21: 3-Table JOIN — Order Items + Product Details

| order_id | product_name | quantity | unit_price | discount_pct |
| --- | --- | --- | --- | --- |
| 1001 | Wireless Earbuds | 2 | 1499.0 | 0.0 |
| 1001 | Laptop Stand | 1 | 899.0 | 10.0 |
| 1002 | Cotton T-Shirt | 1 | 799.0 | 0.0 |
| 1003 | Smart Watch | 1 | 2999.0 | 0.0 |
| 1003 | Running Shoes | 1 | 4599.0 | 5.0 |
| 1004 | Bluetooth Speaker | 1 | 3499.0 | 0.0 |
| 1005 | Smart Watch | 1 | 2999.0 | 0.0 |
| 1006 | Wireless Earbuds | 1 | 1499.0 | 10.0 |
| 1006 | Running Shoes | 1 | 4599.0 | 5.0 |
| 1007 | Bedsheet Set | 1 | 1299.0 | 0.0 |
| 1008 | Laptop Stand | 1 | 899.0 | 0.0 |
| 1009 | Bluetooth Speaker | 1 | 3499.0 | 0.0 |
| 1009 | Cushion Covers (Set) | 2 | 599.0 | 15.0 |
| 1010 | Bedsheet Set | 1 | 1299.0 | 0.0 |
| 1010 | Cushion Covers (Set) | 1 | 599.0 | 0.0 |

---

## SECTION 7 — BUSINESS USE CASES

### Monthly Sales Trend

| month | orders | revenue |
| --- | --- | --- |
| 8.0 | 10.0 | 35085.0 |

### Customer Lifetime Value (CLV)

| customer_id | customer | is_premium | total_orders | lifetime_value |
| --- | --- | --- | --- | --- |
| 103 | Rohan Gupta | True | 2 | 8397.0 |
| 101 | Aarav Sharma | True | 2 | 7997.0 |
| 107 | Karan Mehta | True | 1 | 6098.0 |
| 105 | Vikram Singh | True | 1 | 5898.0 |
| 104 | Sneha Reddy | False | 1 | 2999.0 |
| 108 | Divya Nair | False | 1 | 1598.0 |
| 106 | Ananya Iyer | False | 1 | 1299.0 |
| 102 | Priya Patel | False | 1 | 799.0 |

### Net Revenue Per Product (after discount)

| product_name | category | net_revenue |
| --- | --- | --- |
| Running Shoes | Clothing | 8738.1 |
| Bluetooth Speaker | Electronics | 6998.0 |
| Smart Watch | Electronics | 5998.0 |
| Wireless Earbuds | Electronics | 4347.1 |
| Bedsheet Set | Home | 2598.0 |
| Laptop Stand | Electronics | 1708.1 |
| Cushion Covers (Set) | Home | 1617.3 |
| Cotton T-Shirt | Clothing | 799.0 |

### Duplicate Email Check

_No rows returned._

---

## SECTION 8 — CASE & CONDITIONAL LOGIC

### Q24: Product Price Tiers

| product_name | unit_price | price_tier |
| --- | --- | --- |
| Cushion Covers (Set) | 599.0 | Budget |
| Cotton T-Shirt | 799.0 | Budget |
| Laptop Stand | 899.0 | Budget |
| Bedsheet Set | 1299.0 | Mid-Range |
| Wireless Earbuds | 1499.0 | Mid-Range |
| Smart Watch | 2999.0 | Mid-Range |
| Bluetooth Speaker | 3499.0 | Premium |
| Running Shoes | 4599.0 | Premium |

### Q25: Delivered vs Not Delivered (single row)

| delivered_count | not_delivered_count |
| --- | --- |
| 6.0 | 4.0 |

### Premium vs Standard Customer Revenue

| customer_type | orders | total_revenue |
| --- | --- | --- |
| Premium | 6 | 28390.0 |
| Standard | 4 | 6695.0 |

---

## SECTION 9 — VALIDATION

### Row Counts Final Check

| tbl | rows |
| --- | --- |
| customers | 8 |
| products | 8 |
| orders | 10 |
| order_items | 15 |

### Orphan Order Items Check (should be 0)

| orphan_items |
| --- |
| 0 |

### Total Amount Consistency Check

| order_id | recorded_total | calculated_total |
| --- | --- | --- |
| 1001.0 | 4498.0 | 3807.1 |
| 1002.0 | 799.0 | 799.0 |
| 1003.0 | 7498.0 | 7368.05 |
| 1004.0 | 3499.0 | 3499.0 |
| 1005.0 | 2999.0 | 2999.0 |
| 1006.0 | 5898.0 | 5718.15 |
| 1007.0 | 1299.0 | 1299.0 |
| 1008.0 | 899.0 | 899.0 |
| 1009.0 | 6098.0 | 4517.3 |
| 1010.0 | 1598.0 | 1898.0 |

---
