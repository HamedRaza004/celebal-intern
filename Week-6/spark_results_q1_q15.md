# Spark Architecture & Processing — Results & Insights

> **CEI Summer Internship 2026 — Spark Week Task**
> Dataset: `orders.csv` (300 rows) · `source.csv` (100 rows) — self-generated

---

## Q1 — Driver, Cluster Manager, Executor

| Component | Role | Count |
|---|---|---|
| **Driver** | Runs your code, builds the DAG, coordinates the job | 1 per app |
| **Cluster Manager** | Allocates CPU/memory to the job (YARN / Kubernetes / Standalone) | 1 per cluster |
| **Executor** | Does the actual data processing on worker nodes | Many |

**Flow:** Your code runs on Driver → Driver asks Cluster Manager for resources → Cluster Manager starts Executors → Executors process data and report back to Driver.

---

## Q2 — Lazy Evaluation

Spark doesn't run anything when you write `df.filter().select().groupBy()`. It just builds a plan. Only when you call an **action** (`.show()`, `.count()`, `.write()`) does it look at the entire plan, optimize it, then execute everything in one go.

**Why this helps on large data:** Spark can merge steps, reorder filters, and push conditions closer to the data source — avoiding unnecessary reads. A chain of 10 transformations might execute as just 2 stages instead of 10.

---

## Q3 — Reading CSV

```python
df = spark.read.csv("data/source.csv", header=True, inferSchema=True)
```

**Schema inferred:**

```
root
 |-- product_id: string
 |-- product_name: string
 |-- category: string
 |-- price: double
 |-- stock: integer
 |-- region: string
```

**Sample output (5 rows):**

| product_id | product_name | category | price | stock | region |
|---|---|---|---|---|---|
| P101 | Chair | Furniture | 3350.32 | 363 | East |
| P102 | T-Shirt | Clothing | 197.88 | 107 | South |
| P103 | Python Guide | Books | 2894.87 | 185 | West |
| P104 | Shelf | Furniture | 5457.19 | 443 | Central |
| P105 | Kurta | Clothing | 4621.04 | 117 | Central |

---

## Q4 — CSV vs Parquet

| Feature | CSV | Parquet |
|---|---|---|
| Storage format | Row-based | Columnar |
| Human readable | ✅ Yes | ❌ No (binary) |
| Compression | ❌ None | ✅ Built-in |
| Read one column | ❌ Reads all columns | ✅ Reads only that column |
| Predicate pushdown | ❌ No | ✅ Yes |
| Best for | Sharing / Excel | Analytics / Spark |

**Bottom line:** For a query like `SELECT price WHERE category='Electronics'` on 10GB of data — CSV reads all 10GB, Parquet might read only ~400MB. That's the real-world difference.

---

## Q5 — Electronics: product_id + price

```python
df.select("product_id", "price") \
  .filter(F.col("category") == "Electronics") \
  .show(10)
```

**Output (sample):**

| product_id | price |
|---|---|
| P112 | 4369.01 |
| P117 | 570.24 |
| P120 | 215.08 |
| P131 | 3742.61 |
| P134 | 4063.01 |
| P136 | 1007.69 |
| P141 | 2188.58 |
| P157 | 5330.73 |

Total Electronics products: **17 rows**

---

## Q6 — Rename + Cast

```python
df_revised = df \
    .withColumnRenamed("product_id", "new_name") \
    .withColumn("price", F.col("price").cast(DoubleType()))
```

Schema after changes — `product_id` is now `new_name`, `price` confirmed as `double`.

| new_name | price |
|---|---|
| P101 | 3350.32 |
| P102 | 197.88 |

> **Key concept:** DataFrames are immutable. `df` is unchanged. `df_revised` is a brand new DataFrame.

---

## Q7 — Lineage Graph (DAG) & Fault Tolerance

When a worker node crashes mid-job, Spark checks the lineage (DAG) to see *how* the lost data was computed, then re-runs just those steps on a healthy executor. No full restart needed. The lineage is the recovery plan.

You can inspect the plan with:
```python
df_filtered.explain()
```

---

## Q8 — Completed Orders with Amount > 1000

```python
df_orders.filter(
    (F.col("status") == "Completed") & (F.col("amount") > 1000)
)
```

**Sample output:**

| order_id | user_id | status | amount | category |
|---|---|---|---|---|
| ORD1001 | U1009 | Completed | 11731.88 | Furniture |
| ORD1002 | U1011 | Completed | 7444.51 | Electronics |
| ORD1008 | U1044 | Completed | 15492.18 | Books |
| ORD1013 | U1047 | Completed | 12044.68 | Furniture |
| ORD1015 | U1000 | Completed | 14190.73 | Electronics |

---

## Q9 — Predicate Pushdown in Parquet

When you filter a Parquet file, Spark doesn't load the data first and then filter. Instead, it pushes the filter into the file reader itself. Parquet stores min/max statistics per column chunk — if a chunk's max value is below your filter threshold, the whole chunk is skipped. Data that never loads into RAM = faster query + lower memory usage.

**With CSV:** impossible — must read every byte first, then filter.
**With Parquet:** filter applied at read time, skipping irrelevant chunks.

---

## Q10 — Adding final_price Column (18% Tax)

```python
df_orders.withColumn("final_price", F.round(F.col("base_price") * 1.18, 2))
```

**Output:**

| order_id | base_price | final_price | category |
|---|---|---|---|
| ORD1001 | 9873.16 | 11650.33 | Furniture |
| ORD1002 | 6657.46 | 7855.80 | Electronics |
| ORD1003 | 11717.44 | 13826.58 | Books |
| ORD1005 | 8196.76 | 9672.18 | Electronics |
| ORD1007 | 9109.98 | 10749.78 | Books |

---

## Q11 — Transformations vs Actions

| Type | Examples | When it runs |
|---|---|---|
| **Transformation** | `.filter()`, `.select()`, `.withColumn()`, `.groupBy()`, `.join()` | Never immediately — builds the plan |
| **Action** | `.show()`, `.count()`, `.collect()`, `.write()`, `.first()` | Immediately — triggers execution |

Rule: transformations are lazy, actions are eager. One action can trigger a chain of many transformations all at once.

---

## Q12 — Parquet → Filter Nulls → Save CSV

```python
df_parquet = spark.read.parquet("data/orders_parquet")
df_no_nulls = df_parquet.filter(F.col("user_id").isNotNull())
df_no_nulls.write.option("header","true").csv("data/output_cleaned")
```

| Metric | Count |
|---|---|
| Rows before filter | 300 |
| Rows after removing null user_id | 286 |
| Null user_id rows dropped | 14 |

---

## Q13 — Client Mode vs Cluster Mode

| | Client Mode | Cluster Mode |
|---|---|---|
| Driver runs on | Your machine (outside cluster) | Inside the cluster |
| If you close terminal | Job dies | Job keeps running |
| Good for | Development, notebooks | Production pipelines |
| Debugging | Easy — logs in your terminal | Hard — logs on cluster |
| Network | Driver ↔ Executors over external network | All within cluster network |

---

## Q14 — Region = North OR Priority = High

```python
df_orders.filter(
    (F.col("region") == "North") | (F.col("priority") == "High")
)
```

**Sample output:**

| order_id | region | priority | status | amount |
|---|---|---|---|---|
| ORD1002 | Central | High | Completed | 7444.51 |
| ORD1007 | West | High | Processing | 11879.13 |
| ORD1008 | West | High | Completed | 15492.18 |
| ORD1012 | North | Low | Processing | 4403.41 |
| ORD1016 | North | Medium | Processing | 14158.55 |

---

## Q15 — show(5) vs collect()

| | `.show(5)` | `.collect()` |
|---|---|---|
| Data moved to driver | 5 rows only | Every single row |
| Safe on 1TB dataset | ✅ Yes | ❌ Will crash / OOM |
| Speed | Instant | Slow (full scan + transfer) |
| Use case | Exploration, debugging | Only when data fits in RAM |

```python
# Safe — always use this for exploration
df_orders.show(5)

# Dangerous — never on large data
# data = df_orders.collect()  ← can crash the driver
```

**Sample show(5) output:**

| order_id | user_id | category | status | amount | region |
|---|---|---|---|---|---|
| ORD1001 | U1009 | Furniture | Completed | 11731.88 | Central |
| ORD1002 | U1011 | Electronics | Completed | 7444.51 | Central |
| ORD1003 | U1006 | Books | Cancelled | 12809.10 | South |
| ORD1005 | U1063 | Electronics | Processing | 15206.50 | East |

---

## Full Pipeline Results

**Electronics products after full pipeline (17 rows):**

| product_id | product_name | category | region | price | final_price |
|---|---|---|---|---|---|
| P112 | Laptop | Electronics | Central | 4369.01 | 5155.43 |
| P117 | Laptop | Electronics | West | 570.24 | 672.88 |
| P120 | Headphones | Electronics | West | 215.08 | 253.79 |
| P131 | Smartphone | Electronics | North | 3742.61 | 4416.28 |
| P134 | Smartphone | Electronics | Central | 4063.01 | 4794.35 |
| P157 | Tablet | Electronics | Central | 5330.73 | 6290.26 |

Saved as Parquet at `data/electronics_final.parquet` ✅

---

## Key Performance Insights

**1. Parquet over CSV always for analytics** — on large datasets, Parquet's columnar storage + predicate pushdown can reduce I/O by 80%+.

**2. Lazy evaluation is not just a design choice** — it's the main reason Spark can optimize multi-step pipelines. The same chain in MapReduce would write intermediate files to disk after every step.

**3. Wide transformations are expensive** — `groupBy()`, `distinct()`, `join()` all trigger a shuffle (data moves between executors over the network). Narrow ones like `filter()` and `select()` are cheap (each row processed independently).

**4. Never use collect() in production** — 14 null rows were caught and dropped safely without ever pulling the full dataset to the driver.

**5. Fault tolerance is free** — Spark's lineage graph means if an executor crashes, only the affected partition is recomputed, not the entire job.
