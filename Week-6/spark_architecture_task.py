from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType

spark = SparkSession.builder \
    .appName("SparkArchitectureTask") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")


# ================================================================
# Q1 — Roles: Driver, Cluster Manager, Executor
# ================================================================
# (Theory answer — code demonstrates the session startup above)
#
# DRIVER:
#   The brain of the Spark application. It runs your main()
#   program, builds the DAG (execution plan), and coordinates
#   the whole job. There is exactly ONE driver per application.
#   It talks to the Cluster Manager to request resources.
#
# CLUSTER MANAGER:
#   Acts like an HR department — it allocates resources (CPU,
#   memory) across the cluster. Spark supports three options:
#   Standalone (built-in), YARN (Hadoop), or Kubernetes.
#   It doesn't run your code — it just manages who gets what.
#
# EXECUTOR:
#   The actual workers. Each executor runs on a worker node,
#   holds data partitions in memory, and executes the tasks
#   the Driver sends it. Results are sent back to the Driver.
#   If an executor dies, the Driver detects it and re-schedules
#   the tasks on another executor (fault tolerance).
#
# Flow: Driver → Cluster Manager → Executors → results back to Driver


# ================================================================
# Q2 — Lazy Evaluation
# ================================================================
# (Theory — demonstrated by the fact that nothing runs until
#  an Action like .show() or .count() is called)
#
# Spark does NOT execute transformations immediately.
# When you write df.filter(...).select(...).groupBy(...),
# Spark just builds a plan (DAG) and waits.
# Only when you call an ACTION (.show, .count, .write) does
# Spark look at the entire plan, optimize it (e.g. reordering
# filters, predicate pushdown), and THEN execute it in one go.
#
# Why this helps:
# - Spark can push filters down closer to the data source
#   (read less data from disk)
# - It can combine multiple steps into one stage
# - It avoids running steps that produce data nobody needs
# - On a terabyte dataset, this can save hours of compute time


# ================================================================
# Q3 — Read CSV with header + inferSchema
# ================================================================
# inferSchema=True: Spark scans the data and guesses types.
# header=True: treats row 1 as column names, not data.

df = spark.read.csv(
    "data/source.csv",
    header=True,
    inferSchema=True
)

print("Q3 — Schema after loading source.csv:")
df.printSchema()

print("Q3 — First 5 rows:")
df.show(5)


# ================================================================
# Q4 — CSV vs Parquet
# ================================================================
# (Theory)
#
# CSV — Row-based storage:
#   Every row is stored together on disk.
#   To read just the "price" column from 1 million rows,
#   you still have to read ALL columns of ALL rows.
#   Easy to open in Excel. Human-readable. No compression.
#
# Parquet — Columnar storage:
#   Each column is stored separately on disk.
#   To read just "price", Spark only reads the price column.
#   Also stores min/max stats per column block — so Spark can
#   skip entire row groups that don't match a filter.
#   This is called Predicate Pushdown (see Q9).
#
# Why it matters for performance:
#   A query like SELECT price FROM products WHERE category='Electronics'
#   on a 10GB CSV → reads all 10GB
#   on a 10GB Parquet → might read only 500MB (just price + category)
#   That's 20x less I/O = much faster query


# ================================================================
# Q5 — Select product_id + price where category = 'Electronics'
# ================================================================

print("\nQ5 — Electronics: product_id and price only:")
df.select("product_id", "price") \
  .filter(F.col("category") == "Electronics") \
  .show(10)


# ================================================================
# Q6 — Rename column + cast data type
# ================================================================
# withColumnRenamed(old, new) → renames a column
# withColumn(name, col.cast(type)) → changes data type
# DataFrames are IMMUTABLE — these return new DataFrames

df_revised = df \
    .withColumnRenamed("product_id", "new_name") \
    .withColumn("price", F.col("price").cast(DoubleType()))

print("\nQ6 — After rename (product_id → new_name) + cast price to Double:")
df_revised.printSchema()
df_revised.select("new_name", "price").show(5)


# ================================================================
# Q7 — Lineage Graph (DAG) and Fault Tolerance
# ================================================================
# (Theory)
#
# Every transformation you apply is recorded in a DAG
# (Directed Acyclic Graph) — basically a recipe that says
# "to get DataFrame C, I took DataFrame A, filtered it (B),
# then grouped it (C)".
#
# If a worker node crashes mid-job and loses its data:
# - Spark does NOT need to restart from scratch
# - It looks at the lineage graph and says:
#   "I know how C was made — I'll just re-run those steps"
# - It re-creates only the lost partition, from the source
#
# This is why Spark doesn't need replication like HDFS does.
# The lineage IS the backup plan.
#
# You can see the lineage for any DataFrame:
print("\nQ7 — Lineage (DAG) for a transformed DataFrame:")
df_filtered = df.filter(F.col("category") == "Electronics") \
                .select("product_id", "price")
print(df_filtered.explain())  # prints the physical execution plan


# ================================================================
# Q8 — Filter: status = 'Completed' AND amount > 1000
# ================================================================

df_orders = spark.read.csv(
    "data/orders.csv",
    header=True,
    inferSchema=True
)

print("\nQ8 — Completed orders with amount > 1000:")
df_orders.filter(
    (F.col("status") == "Completed") & (F.col("amount") > 1000)
).select("order_id", "user_id", "status", "amount", "category") \
 .show(10)


# ================================================================
# Q9 — Predicate Pushdown in Parquet
# ================================================================
# (Theory)
#
# When reading a Parquet file, Spark can push the filter
# condition INSIDE the file reader — before loading data
# into memory.
#
# Parquet stores column statistics (min value, max value,
# null count) for every "row group" (chunk of rows).
# If a filter says price > 5000, and a row group has
# max_price = 3000, Spark skips that entire row group.
# Never loads it into memory at all.
#
# With CSV: impossible — Spark must read every byte first,
# load it into memory, THEN apply the filter.
#
# Demo — save as parquet and read with a filter:
df_orders.write.mode("overwrite").parquet("data/orders_parquet")
df_parquet = spark.read.parquet("data/orders_parquet")

print("\nQ9 — Reading from Parquet with filter (predicate pushdown active):")
df_parquet.filter(F.col("amount") > 10000) \
          .select("order_id", "amount", "status") \
          .show(5)
# Spark pushes the amount > 10000 filter into the parquet reader
# — row groups where max(amount) <= 10000 are skipped entirely.


# ================================================================
# Q10 — Add new column: final_price = base_price * 1.18
# ================================================================
# withColumn() adds or replaces a column.
# F.round() keeps it to 2 decimal places.

print("\nQ10 — Adding final_price column (18% tax on base_price):")
df_orders \
    .filter(F.col("base_price").isNotNull()) \
    .withColumn("final_price", F.round(F.col("base_price") * 1.18, 2)) \
    .select("order_id", "base_price", "final_price", "category") \
    .show(8)


# ================================================================
# Q11 — Transformations vs Actions
# ================================================================
# (Theory)
#
# TRANSFORMATIONS — lazy, return a new DataFrame, nothing runs:
#   .filter()      → keeps rows matching condition
#   .select()      → picks specific columns
#   .withColumn()  → adds/modifies a column
#   .groupBy()     → groups rows by key
#   .join()        → combines two DataFrames
#   .orderBy()     → sorts rows
#
# ACTIONS — trigger actual execution, return results:
#   .show()        → prints rows to console
#   .count()       → returns number of rows
#   .collect()     → pulls all data to driver (use carefully!)
#   .write()       → saves to disk
#   .first()       → returns first row
#
# The key rule: nothing actually runs until you hit an action.
# Spark builds up the full plan, optimizes it, then executes.

print("\nQ11 — Demonstrating: only the action triggers execution:")
# This line does nothing yet (transformation):
lazy_df = df_orders.filter(F.col("status") == "Completed") \
                   .select("order_id", "amount")
# This line actually runs it (action):
print(f"  Completed order count: {lazy_df.count()}")


# ================================================================
# Q12 — Load Parquet → filter null user_id → save as CSV
# ================================================================

print("\nQ12 — Load Parquet, drop null user_id, save CSV:")
df_from_parquet = spark.read.parquet("data/orders_parquet")
df_no_nulls = df_from_parquet.filter(F.col("user_id").isNotNull())

before = df_from_parquet.count()
after  = df_no_nulls.count()
print(f"  Rows before: {before}  |  After removing null user_id: {after}")

df_no_nulls.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv("data/output_cleaned")

print("  Saved to data/output_cleaned/ successfully")


# ================================================================
# Q13 — Client Mode vs Cluster Mode
# ================================================================
# CLIENT MODE:
#   The Driver runs on the machine that submitted the job
#   (usually your laptop or edge node — outside the cluster).
#   Pros: easy to debug, you see logs directly in your terminal.
#   Cons: if your laptop loses connection, the job dies.
#         Driver ↔ Executor network traffic goes over WAN.
#   Use when: interactive development, Jupyter notebooks.
#
# CLUSTER MODE:
#   The Driver runs INSIDE the cluster on a worker node.
#   Once submitted, you can close your terminal — the job
#   keeps running inside the cluster.
#   Pros: more stable, better network (driver near executors).
#   Cons: harder to debug, logs are on the cluster.
#   Use when: production jobs, scheduled pipelines.
#
# Example submit command:
#   Client mode:  spark-submit --deploy-mode client  job.py
#   Cluster mode: spark-submit --deploy-mode cluster job.py


# ================================================================
# Q14 — Filter: region = 'North' OR priority = 'High'
# ================================================================

print("\nQ14 — Orders from North region OR High priority:")
df_orders.filter(
    (F.col("region") == "North") | (F.col("priority") == "High")
).select("order_id", "region", "priority", "status", "amount") \
 .show(10)


# ================================================================
# Q15 — show(5) vs collect() — why show() is safer
# ================================================================
# .collect():
#   Pulls EVERY row from every executor into the Driver's memory.
#   On a 2TB dataset: that's 2TB into your driver RAM → crash.
#   It's also slow — all data moves over the network.
#   Never use in production on large data.
#
# .show(5):
#   Only fetches 5 rows. Everything else stays on the executors.
#   Driver memory is barely touched.
#   This is always safe, no matter how big the dataset.
#
# Rule of thumb:
#   Use show() to explore → count() for size → write() to save
#   Never collect() unless you're SURE the data fits in memory.

print("\nQ15 — Safe exploration with show(5):")
df_orders.show(5)

print("\nQ15 — Unsafe alternative (DO NOT use on large data):")
print("  # small_sample = df_orders.collect()  ← would crash on TB-scale data")
print("  # Instead use:")
print("  # df_orders.show(5)      ← fetches only 5 rows to driver")
print("  # df_orders.limit(10)    ← creates a limited DataFrame")
print("  # df_orders.count()      ← just a number, no data movement")


# ================================================================
# FULL PIPELINE — Read → Transform → Filter → Write
# ================================================================
# Everything from Q3 to Q12 chained into one clean pipeline.

print("\n=== FULL PIPELINE ===")

final_df = spark.read.csv(
        "data/source.csv", header=True, inferSchema=True   # Q3
    ) \
    .withColumnRenamed("product_id", "new_name") \          # Q6 rename
    .withColumn("price", F.col("price").cast(DoubleType())) \# Q6 cast
    .filter(F.col("category") == "Electronics") \           # Q5 filter
    .filter(F.col("price").isNotNull()) \                   # null safety
    .withColumn(                                            # Q10 new col
        "final_price",
        F.round(F.col("price") * 1.18, 2)
    ) \
    .select("new_name","product_name","category",
            "region","price","final_price")

print("Pipeline result — Electronics with 18% tax applied:")
final_df.show(10)
print(f"Total rows in final output: {final_df.count()}")

# Save as Parquet (best format for downstream queries)
final_df.write.mode("overwrite").parquet("data/electronics_final.parquet")
print("Saved to data/electronics_final.parquet")

spark.stop()
print("\nAll done!")
