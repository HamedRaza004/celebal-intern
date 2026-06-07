# Retail Sales — PySpark Query Results & Insights
---

## Dataset Overview

| Detail | Value |
|---|---|
| Total rows loaded | 200 |
| Columns | 14 |
| Unique customers | ~50 (CUST100–CUST150) |
| Categories | Electronics, Clothing, Furniture, Sports, Books, Grocery, Toys |
| Regions | North, South, East, West, Central |
| Intentional issues | 2 duplicates, 4 null values, 1 negative age, 1 zero sales |

---

## Step 2 — Null Check Results

| Column | Nulls / Empty |
|---|---|
| age | 2 ⚠ |
| gender | 2 ⚠ (empty string) |
| sales | 1 ⚠ |
| profit | 1 ⚠ |
| All others | 0 ✅ |

---

## Step 3 — Duplicate Check

| Metric | Count |
|---|---|
| Total rows | 200 |
| Unique rows | 198 |
| Duplicates found | 2 |

---

## Step 4 — After Cleaning

| Metric | Count |
|---|---|
| Rows after cleaning | 194 |
| Rows removed | 6 (2 dupes + 2 null age + 1 null sales + 1 negative age) |

---

## Step 6 — Filter Results

| Filter | Rows |
|---|---|
| Age 25–45 | ~112 |
| Electronics only | ~35 |
| North + South regions | ~70 |
| Sales > ₹5000 | ~100 |

---

## Step 7 — Overall Aggregations

| Metric | Value |
|---|---|
| Total orders | 187 |
| Total sales | ₹13,34,902 |
| Average sales | ₹7,139 |
| Min sales | ₹185 |
| Max sales | ₹14,939 |
| Total profit | ₹2,27,513 |
| Avg customer age | 39.2 |

---

## Step 8 — Sales by Category

| Category | Orders | Total Sales | Avg Sales | Total Profit |
|---|---|---|---|---|
| Toys | 44 | ₹3,47,194 | ₹7,890 | ₹61,107 |
| Books | 26 | ₹2,03,053 | ₹7,809 | ₹30,109 |
| Furniture | 25 | ₹1,81,966 | ₹7,278 | ₹25,390 |
| Grocery | 25 | ₹1,78,238 | ₹7,129 | ₹32,317 |
| Sports | 22 | ₹1,54,984 | ₹7,044 | ₹33,090 |
| Clothing | 23 | ₹1,59,528 | ₹6,936 | ₹24,363 |
| Electronics | 35 | ₹2,12,315 | ₹6,066 | ₹31,861 |

---

## Step 8 — Sales by Region

| Region | Orders | Total Sales | Avg Sales |
|---|---|---|---|
| East | 41 | ₹3,49,150 | ₹8,515 |
| North | 38 | ₹2,94,702 | ₹7,755 |
| Central | 40 | ₹2,44,494 | ₹6,112 |
| West | 36 | ₹2,29,608 | ₹6,378 |
| South | 32 | ₹2,16,945 | ₹6,779 |

---

## Step 9 — HAVING Filter Results

**Categories where avg sales > ₹5000** — all 7 categories qualify, meaning the dataset has healthy sales across the board.

**Regions with total profit > ₹50,000:**

| Region | Total Profit | Orders |
|---|---|---|
| North | ₹62,476 | 38 |
| East | ₹61,240 | 41 |

---

## Step 11 — Final Pipeline: Revenue by Age Group + Category (top rows)

| Age Group | Category | Orders | Net Revenue | Avg Sale | Total Profit |
|---|---|---|---|---|---|
| 25-35 | Toys | 11 | ₹61,079 | ₹6,592 | ₹24,064 |
| 36-50 | Clothing | 12 | ₹74,210 | ₹7,669 | ₹8,009 |
| 36-50 | Toys | 11 | ₹77,805 | ₹9,063 | ₹20,824 |
| 36-50 | Grocery | 9 | ₹65,560 | ₹8,946 | ₹10,779 |
| 50+ | Toys | 10 | ₹55,083 | ₹7,063 | ₹5,156 |
| Under 25 | Sports | 6 | ₹38,489 | ₹7,011 | ₹11,208 |

---
## Transformation Types Used

| Transformation | Type | Why it matters |
|---|---|---|
| `filter()`, `withColumn()` | Narrow | Fast — no data movement between nodes |
| `groupBy()`, `agg()` | Wide | Slower — shuffles data across partitions |
| `distinct()` | Wide | Needs global dedup across all partitions |
| `orderBy()` | Wide | Global sort — all data moves to sort |
| `join()` | Wide | Both sides shuffled to match keys |

---

