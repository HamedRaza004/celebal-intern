from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType


spark = (
    SparkSession.builder.appName("RetailSalesAnalysis")
    .master("local[*]")
    .config("spark.driver.memory", "2g")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")
print("Spark session started!")


df_raw = spark.read.csv("retail_sales.csv", header=True, inferSchema=True)

print(f"Rows loaded  : {df_raw.count()}")
print(f"Columns      : {len(df_raw.columns)}")

df_raw.printSchema()

df_raw.show(5, truncate=False)


print("=== Null Check ===")
null_counts = [
    (c, df_raw.filter(F.col(c).isNull() | (F.col(c).cast("string") == "")).count())
    for c in df_raw.columns
]

for col, cnt in null_counts:
    print(f"  {col:<20} → {cnt} nulls/empty")


total = df_raw.count()
unique = df_raw.dropDuplicates().count()
print(f"Total rows : {total}")
print(f"Unique rows: {unique}")
print(f"Duplicates : {total - unique}")


df_clean = (
    df_raw.dropDuplicates()
    .filter(F.col("sales").isNotNull() & (F.col("sales") > 0))
    .filter(F.col("age").isNotNull() & (F.col("age") > 0) & (F.col("age") <= 100))
    .withColumn(
        "gender",
        F.when(
            (F.col("gender").isNull()) | (F.col("gender") == ""), "Unknown"
        ).otherwise(F.col("gender")),
    )
    .withColumn(
        "profit", F.when(F.col("profit").isNull(), 0.0).otherwise(F.col("profit"))
    )
)

print(f"Rows after cleaning : {df_clean.count()}")
print(f"Rows removed        : {total - df_clean.count()}")
df_clean.show(5, truncate=False)


df = (
    df_clean.withColumn("sales", F.col("sales").cast(DoubleType()))
    .withColumn("profit", F.col("profit").cast(DoubleType()))
    .withColumn("discount", F.col("discount").cast(DoubleType()))
    .withColumn("age", F.col("age").cast(IntegerType()))
    .withColumn("join_date", F.to_date(F.col("join_date"), "yyyy-MM-dd"))
    .withColumnRenamed("customer_name", "cust_name")
    .withColumnRenamed("sales", "sale_amount")
)

df.printSchema()


# Filter by age range
df_age = df.filter((F.col("age") >= 25) & (F.col("age") <= 45))
print(f"Age 25–45 rows: {df_age.count()}")

# Filter by category
df_elec = df.filter(F.col("category") == "Electronics")
print(f"Electronics rows: {df_elec.count()}")

# Filter by multiple regions using isin()
df_north_south = df.filter(F.col("region").isin("North", "South"))
print(f"North + South rows: {df_north_south.count()}")

# Filter high-value orders
df_high = df.filter(F.col("sale_amount") > 5000)
print(f"Sales > 5000 rows: {df_high.count()}")

# Combined filter — multiple conditions together
df.filter(
    (F.col("category") == "Electronics")
    & (F.col("region").isin("North", "South"))
    & (F.col("age").between(25, 45))
    & (F.col("sale_amount") > 5000)
).select("cust_name", "region", "category", "sale_amount", "age").show(5)


df.agg(
    F.count("*").alias("total_orders"),
    F.round(F.sum("sale_amount"), 2).alias("total_sales"),
    F.round(F.avg("sale_amount"), 2).alias("avg_sales"),
    F.round(F.min("sale_amount"), 2).alias("min_sales"),
    F.round(F.max("sale_amount"), 2).alias("max_sales"),
    F.round(F.sum("profit"), 2).alias("total_profit"),
    F.round(F.avg("age"), 1).alias("avg_customer_age"),
).show()


# By category
df.groupBy("category").agg(
    F.count("*").alias("orders"),
    F.round(F.sum("sale_amount"), 2).alias("total_sales"),
    F.round(F.avg("sale_amount"), 2).alias("avg_sales"),
    F.round(F.sum("profit"), 2).alias("total_profit"),
).orderBy(F.desc("total_sales")).show()

# By region
df.groupBy("region").agg(
    F.count("*").alias("orders"),
    F.round(F.sum("sale_amount"), 2).alias("total_sales"),
    F.round(F.avg("sale_amount"), 2).alias("avg_sales"),
).orderBy(F.desc("total_sales")).show()

# By region + category (multi-column groupBy)
df.groupBy("region", "category").agg(
    F.count("*").alias("orders"), F.round(F.sum("sale_amount"), 2).alias("total_sales")
).orderBy("region", "category").show(30)


df.groupBy("category").agg(F.round(F.avg("sale_amount"), 2).alias("avg_sales")).filter(
    F.col("avg_sales") > 5000
).orderBy(F.desc("avg_sales")).show()

# Regions with total profit > 50000
df.groupBy("region").agg(
    F.round(F.sum("profit"), 2).alias("total_profit"), F.count("*").alias("orders")
).filter(F.col("total_profit") > 50000).orderBy(F.desc("total_profit")).show()


df.select("region").distinct().show()


df.select("cust_name", "category", "sale_amount", "region").orderBy(
    F.desc("sale_amount")
).show(10)


region_counts = df.groupBy("region").agg(F.count("*").alias("region_order_count"))

df.join(region_counts, on="region", how="left").select(
    "cust_name", "region", "category", "sale_amount", "region_order_count"
).show(5)


final = (
    spark.read.csv("retail_sales.csv", header=True, inferSchema=True)
    .dropDuplicates()
    .filter(F.col("sales").isNotNull() & (F.col("sales") > 0))
    .filter(F.col("age").isNotNull() & (F.col("age") > 0) & (F.col("age") <= 100))
    .withColumn(
        "gender",
        F.when(
            (F.col("gender").isNull()) | (F.col("gender") == ""), "Unknown"
        ).otherwise(F.col("gender")),
    )
    .withColumn(
        "profit", F.when(F.col("profit").isNull(), 0.0).otherwise(F.col("profit"))
    )
    .withColumn("sales", F.col("sales").cast(DoubleType()))
    .withColumn("profit", F.col("profit").cast(DoubleType()))
    .withColumn("discount", F.col("discount").cast(DoubleType()))
    .withColumn("age", F.col("age").cast(IntegerType()))
    .withColumn("join_date", F.to_date(F.col("join_date"), "yyyy-MM-dd"))
    .withColumnRenamed("customer_name", "cust_name")
    .withColumnRenamed("sales", "sale_amount")
    .withColumn("discount_pct", F.round(F.col("discount") * 100, 1))
    .withColumn(
        "net_revenue", F.round(F.col("sale_amount") * (1 - F.col("discount")), 2)
    )
    .withColumn(
        "age_group",
        F.when(F.col("age") < 25, "Under 25")
        .when(F.col("age").between(25, 35), "25-35")
        .when(F.col("age").between(36, 50), "36-50")
        .otherwise("50+"),
    )
)

# Preview
final.select(
    "cust_name",
    "age_group",
    "region",
    "category",
    "sale_amount",
    "net_revenue",
    "profit",
    "gender",
).show(8)

# Final aggregation — Revenue breakdown by Age Group + Category
final.groupBy("age_group", "category").agg(
    F.count("*").alias("orders"),
    F.round(F.sum("net_revenue"), 2).alias("net_revenue"),
    F.round(F.avg("sale_amount"), 2).alias("avg_sale"),
    F.round(F.sum("profit"), 2).alias("total_profit"),
).orderBy("age_group", "category").show(30)

# Top 10 customers by net revenue
final.groupBy("customer_id", "cust_name").agg(
    F.count("*").alias("orders"),
    F.round(F.sum("net_revenue"), 2).alias("total_net_revenue"),
    F.round(F.sum("profit"), 2).alias("total_profit"),
).orderBy(F.desc("total_net_revenue")).show(10)

spark.stop()
print("Done!")
