# 🛍️ Shopping Analysis — Quick Summary

**Dataset:** Myntra Shopping Dataset (from Kaggle)  
**Tool:** Python + Pandas  
**Goal:** Load, clean, and make sense of the product data

---

## What This Notebook Does

It walks through a standard data cleaning and exploration workflow in 7 steps:

1. **Load the data** — reads a pre-combined CSV file (or optionally merges multiple category-wise CSVs using `glob`)
2. **Explore the structure** — checks shape, column names, data types, and basic stats to get a feel for the dataset
3. **Handle missing values** — fills numeric columns with their median and text columns with `"Unknown"`
4. **Filter & slice** — pulls out subsets like products priced above ₹500, items rated 4.0+, or a specific category (e.g. t-shirts)
5. **Remove duplicates** — drops repeated rows and also deduplicates by `product_id`
6. **Create a derived column** — since there's no quantity in the raw data, it simulates one (random 1–5) and computes `total_amount = final_price × quantity`
7. **Save the result** — exports the cleaned, enriched dataset to a new CSV file

---

## Key Columns

| Column | What it is |
|---|---|
| `product_id` | Unique product identifier |
| `title` | Product name |
| `category` | Product category (e.g. tshirts, jeans) |
| `initial_price` | Original listed price (₹) |
| `discount` | Discount percentage |
| `final_price` | Price after discount |
| `rating` | Customer rating (out of 5) |
| `ratings_count` | Number of reviews |

---

## Takeaway

This is a solid, well-structured data prep notebook — good for anyone learning Pandas or wanting a clean starting point before doing deeper analysis or visualization on a retail/e-commerce dataset.
