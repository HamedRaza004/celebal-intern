# E-Commerce Order Analytics System

A full-featured Python + SQLite analytics system with a beautiful Rich CLI.

## Requirements

```
pip install rich
```

## Quick Start

```bash
python main.py
```

On first launch, choose **Option 1 → Setup Wizard** to generate data, clean it, and load it into SQLite.

## Project Structure

```
├── main.py              # CLI entry point (run this)
├── generate_data.py     # Part 1: Generates 4 CSV files with intentional data issues
├── clean_data.py        # Part 2: Cleans orders, products, customers, order_items
├── queries.py           # Part 3: All 16 SQL queries (Basic → Advanced)
├── report_generator.py  # Part 4: Python+SQL period-based reports
├── edge_cases.py        # Part 5: 4 edge case test functions
└── data/
    ├── raw/             # Generated CSVs
    ├── clean/           # Cleaned CSVs
    ├── ecommerce.db     # SQLite database
    └── cleaning_report.txt
```

## Features

### Part 1 — Data Generation
- 500 customers, 200 products, 600 orders, 1400+ order items
- Intentional issues: 5% NULL customer_ids, 3% negative quantities, wrong date formats, bad emails, messy product names

### Part 2 — Data Cleaning
- `clean_orders()` — fixes date formats, fills NULL customer_ids
- `clean_products()` — normalizes product names (title case, trim whitespace)
- `validate_emails()` — flags invalid emails
- `check_referential_integrity()` — removes orphan order_items

### Part 3 — SQL Analysis (16 queries)
- **Basic**: revenue per category, top 10 customers, monthly order counts
- **Intermediate**: undelivered customers, return-heavy products, return rates
- **Advanced**: running totals, DENSE_RANK, LAG/LEAD, multi-level CTEs, NTILE, YoY comparison, cohort analysis, cumulative distribution, market basket analysis

### Part 4 — Report Generator
- Daily / Weekly / Monthly reports
- Total orders, revenue, unique customers
- Top 3 products + % change vs previous period

### Part 5 — Edge Case Tests
- Orphan order_id in order_items
- discount_percent > 100 detection
- Zero quantity revenue impact
- Future order_date detection
