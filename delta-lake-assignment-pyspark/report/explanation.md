# Delta Lake MERGE Implementation (PySpark / Databricks) - Short Explanation

**Dataset:** Sample Superstore (9,994 rows, 21 columns)
**Tool:** PySpark + Delta Lake (`delta.tables.DeltaTable`), run on Databricks.

## What was done

The raw CSV was loaded into Spark and written into a Delta table. 

From there, the cleaning pass checked for nulls (none found) and fully duplicate rows (none found
either), but text columns still got a `trim()` pass for stray whitespace, and Order Date / Ship
Date were converted from plain strings into actual date types. The cleaned DataFrame was written
back over the Delta table with `overwriteSchema` set, since the date columns changed type.

To simulate an incremental load, a 25-row batch was built mixing two things you'd see in a real
daily refresh: 15 rows pulled from the existing data with Quantity, Discount, Sales and Profit
bumped (corrections to existing orders), and 10 brand new order rows with fresh Row IDs (new
sales). Two of those rows were deliberately duplicated and then dropped again before the merge,
to confirm the cleaning logic holds up on incoming batches too, not just the initial load.

The MERGE joins on `Row ID`: matched rows get `whenMatchedUpdateAll()`, unmatched rows get
`whenNotMatchedInsertAll()`. After running it, the table grew from 9,994 to 10,004 rows - exactly
the 10 new orders - while the 15 matching rows were updated in place.

## Validation

- Row count before/after: 9,994 -> 10,004 (net +10, matching the 10 new rows)
- `Row ID` duplicate count after merge: 0
- Spot check on one of the updated rows confirmed the table reflects the new
  Quantity/Discount/Sales/Profit from the incremental batch
- Spot check on a newly inserted row confirmed it landed in the table correctly

## Why MERGE instead of a plain append/overwrite

A plain append would have created a second copy of the 15 updated rows instead of correcting
them, and an overwrite would mean rebuilding the whole table every refresh. MERGE keeps the
9,979 untouched rows as they are, updates exactly the rows that changed, and inserts only what's
genuinely new.


