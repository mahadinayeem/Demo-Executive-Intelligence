import polars as pl
import numpy as np
import json
import math
import sys
import os

# Set UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

print("--- Starting Module 1 Data Processing with Polars ---")

# 1. Load Datasets
dept_path = r"E:\ITL FINAL ADV ANALYSIS\itl_dept.csv"
checkings_path = r"E:\ITL FINAL ADV ANALYSIS\itl_checkings.csv"
orders_path = r"E:\ITL FINAL ADV ANALYSIS\itl_orders.csv"

# Load itl_dept
print("Reading itl_dept.csv...")
df_dept = pl.read_csv(
    dept_path,
    infer_schema_length=10000,
    ignore_errors=True,
    truncate_ragged_lines=True
).select([
    pl.col("id").cast(pl.Utf8).alias("dept_id"),
    pl.col("name").alias("outlet_name"),
    pl.col("code").alias("outlet_code"),
    pl.col("territory_id").cast(pl.Utf8).alias("territory_id"),
    pl.col("department_type_id").cast(pl.Utf8).alias("department_type_id"),
    pl.col("lat").cast(pl.Float64, strict=False).alias("lat"),
    pl.col("long").cast(pl.Float64, strict=False).alias("long"),
    pl.col("status").alias("status"),
    pl.col("is_visitable").alias("is_visitable"),
    pl.col("address").alias("address")
])

# Load itl_orders
print("Reading itl_orders.csv...")
df_orders = pl.read_csv(
    orders_path,
    infer_schema_length=10000,
    ignore_errors=True,
    truncate_ragged_lines=True
).select([
    pl.col("order_id").cast(pl.Utf8),
    pl.col("order_date").cast(pl.Utf8),
    pl.col("buyer_department_id").cast(pl.Utf8).alias("dept_id"),
    pl.col("buyer_department_name").alias("buyer_dept_name"),
    pl.col("buyer_department_territory").cast(pl.Utf8).alias("buyer_territory"),
    pl.col("seller_department_id").cast(pl.Utf8).alias("seller_id"),
    pl.col("seller_department_name").alias("seller_name"),
    pl.col("seller_department_territory").cast(pl.Utf8).alias("seller_territory"),
    pl.col("amount").cast(pl.Float64, strict=False).alias("amount"),
    pl.col("order_qty").cast(pl.Float64, strict=False).alias("order_qty"),
    pl.col("created_id").cast(pl.Utf8).alias("sr_id"),
    pl.col("created_name").alias("sr_name"),
    pl.col("product_sku").alias("product_sku"),
    pl.col("product_category_name").alias("category_name")
])

# Filter out erroneous order amounts if any
# Check distribution of amount
print(f"Total Raw Order amount: {df_orders.select(pl.col('amount').sum()).item():,.2f}")

# Compute Outlet Aggregates from Orders
print("Aggregating Orders by Outlet...")
outlet_sales = df_orders.group_by("dept_id").agg([
    pl.col("amount").sum().alias("total_revenue"),
    pl.col("order_id").n_unique().alias("total_orders"),
    pl.col("order_qty").sum().alias("total_units"),
    pl.col("product_sku").n_unique().alias("unique_skus"),
    pl.col("order_date").min().alias("first_order_date"),
    pl.col("order_date").max().alias("last_order_date"),
    pl.col("sr_id").first().alias("order_sr_id"),
    pl.col("sr_name").first().alias("order_sr_name"),
    pl.col("seller_name").first().alias("distributor_name")
])

# Load itl_checkings
print("Reading itl_checkings.csv...")
df_checkings = pl.read_csv(
    checkings_path,
    infer_schema_length=10000,
    ignore_errors=True,
    truncate_ragged_lines=True
).select([
    pl.col("id").cast(pl.Utf8).alias("checking_id"),
    pl.col("department_id").cast(pl.Utf8).alias("dept_id"),
    pl.col("user_id").cast(pl.Utf8).alias("sr_id"),
    pl.col("lat").cast(pl.Float64, strict=False).alias("checkin_lat"),
    pl.col("long").cast(pl.Float64, strict=False).alias("checkin_long"),
    pl.col("checked_out_at").alias("checked_out_at"),
    pl.col("created_at").alias("visit_time"),
    pl.col("checkin_distance").cast(pl.Float64, strict=False).alias("checkin_distance"),
    pl.col("check_in_address").alias("check_in_address")
])

# Compute Outlet Aggregates from Checkings
print("Aggregating Checkings by Outlet...")
outlet_visits = df_checkings.group_by("dept_id").agg([
    pl.col("checking_id").count().alias("total_visits"),
    pl.col("sr_id").n_unique().alias("unique_srs_visited"),
    pl.col("sr_id").first().alias("primary_sr_id"),
    pl.col("visit_time").min().alias("first_visit_time"),
    pl.col("visit_time").max().alias("last_visit_time")
])

# Merge Dept with Sales & Visits
print("Merging master outlet profile...")
df_master = df_dept.join(outlet_sales, on="dept_id", how="left")
df_master = df_master.join(outlet_visits, on="dept_id", how="left")

# Fill NAs
df_master = df_master.with_columns([
    pl.col("total_revenue").fill_null(0.0),
    pl.col("total_orders").fill_null(0),
    pl.col("total_units").fill_null(0.0),
    pl.col("unique_skus").fill_null(0),
    pl.col("total_visits").fill_null(0),
    pl.col("unique_srs_visited").fill_null(0)
])

# Save summary stats
total_registered = len(df_master)
total_active = df_master.filter(pl.col("total_orders") > 0).height
total_visited = df_master.filter(pl.col("total_visits") > 0).height
total_unvisited = df_master.filter(pl.col("total_visits") == 0).height
visited_but_no_order = df_master.filter((pl.col("total_visits") > 0) & (pl.col("total_orders") == 0)).height
order_without_visit = df_master.filter((pl.col("total_visits") == 0) & (pl.col("total_orders") > 0)).height
total_rev = df_master.select(pl.col("total_revenue").sum()).item()

print("\n=== OVERALL SUMMARY ===")
print(f"Total Registered Outlets: {total_registered:,}")
print(f"Total Active Outlets (with >= 1 Order): {total_active:,} ({total_active/total_registered*100:.2f}%)")
print(f"Total Visited Outlets: {total_visited:,} ({total_visited/total_registered*100:.2f}%)")
print(f"Total Unvisited Outlets (Blind Spots): {total_unvisited:,} ({total_unvisited/total_registered*100:.2f}%)")
print(f"Visited but Zero Orders (Conversion Failure): {visited_but_no_order:,}")
print(f"Orders Without Visit Log: {order_without_visit:,}")
print(f"Total Revenue Generated: BDT {total_rev:,.2f}")

# 1. Territory Aggregates
territory_stats = df_master.group_by("territory_id").agg([
    pl.col("dept_id").count().alias("registered_outlets"),
    (pl.col("total_orders") > 0).sum().alias("active_outlets"),
    (pl.col("total_visits") > 0).sum().alias("visited_outlets"),
    (pl.col("total_visits") == 0).sum().alias("unvisited_outlets"),
    pl.col("total_visits").sum().alias("total_visits_sum"),
    pl.col("total_orders").sum().alias("total_orders_sum"),
    pl.col("total_revenue").sum().alias("total_revenue_bdt")
]).sort("total_revenue_bdt", descending=True)

territory_stats.write_csv(r"E:\ITL FINAL ADV ANALYSIS\territory_analytics_summary.csv")
print("Territory summary exported. Total territories:", len(territory_stats))

# 2. SR Movement Analysis
sr_stats = df_checkings.group_by("sr_id").agg([
    pl.col("checking_id").count().alias("visit_count"),
    pl.col("dept_id").n_unique().alias("unique_outlets_visited"),
    pl.col("visit_time").n_unique().alias("unique_visit_events")
]).sort("visit_count", descending=True)

sr_stats.write_csv(r"E:\ITL FINAL ADV ANALYSIS\sr_analytics_summary.csv")
print("SR summary exported. Total SRs:", len(sr_stats))

# 3. Top 300 Micro-Hubs (Density grid)
micro_hubs = df_master.filter(
    pl.col("lat").is_not_null() & 
    pl.col("long").is_not_null() &
    (pl.col("lat") > 20.0) & (pl.col("lat") < 27.0) &
    (pl.col("long") > 88.0) & (pl.col("long") < 93.0)
).with_columns([
    pl.col("lat").round(3).alias("lat_grid"),
    pl.col("long").round(3).alias("long_grid")
]).group_by(["lat_grid", "long_grid", "territory_id"]).agg([
    pl.col("dept_id").count().alias("outlet_count"),
    pl.col("total_revenue").sum().alias("hub_revenue"),
    pl.col("total_visits").sum().alias("hub_visits"),
    pl.col("total_orders").sum().alias("hub_orders")
]).sort("hub_revenue", descending=True)

micro_hubs.head(300).write_csv(r"E:\ITL FINAL ADV ANALYSIS\top_300_micro_hubs.csv")
print("Top 300 Micro-Hubs exported.")

# 4. Blind Spots Sample
blind_spots = df_master.filter(pl.col("total_visits") == 0).select([
    "dept_id", "outlet_name", "outlet_code", "territory_id", "address", "distributor_name"
]).head(500)
blind_spots.write_csv(r"E:\ITL FINAL ADV ANALYSIS\blind_spots_sample.csv")

# 5. Visited Non-Ordered Outlets
visited_non_ordered = df_master.filter((pl.col("total_visits") >= 3) & (pl.col("total_orders") == 0)).select([
    "dept_id", "outlet_name", "outlet_code", "territory_id", "total_visits", "address"
]).sort("total_visits", descending=True).head(500)
visited_non_ordered.write_csv(r"E:\ITL FINAL ADV ANALYSIS\high_visit_zero_order_outlets.csv")

print("\n--- Module 1 Initial Aggregation Complete Successfully! ---")
