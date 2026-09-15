import polars as pl
import numpy as np
import json
import math
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

print("--- Running Comprehensive Module 1 Geospatial Analytics Engine ---")

dept_path = r"E:\ITL FINAL ADV ANALYSIS\itl_dept.csv"
checkings_path = r"E:\ITL FINAL ADV ANALYSIS\itl_checkings.csv"
orders_path = r"E:\ITL FINAL ADV ANALYSIS\itl_orders.csv"

# 1. Load and clean orders
print("Processing clean orders...")
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
    pl.col("product_category_name").alias("category_name"),
    pl.col("order_status").alias("order_status")
]).filter(
    (pl.col("order_qty") < 1000000) & 
    (pl.col("amount") < 5000000) &
    (pl.col("order_status").is_in(["accepted", "delivered"]))
)

# 2. Load and clean dept
print("Processing outlet master...")
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

# 3. Load and clean checkings
print("Processing checkings...")
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

# Aggregate Sales by Outlet
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

# Aggregate Visits by Outlet
outlet_visits = df_checkings.group_by("dept_id").agg([
    pl.col("checking_id").count().alias("total_visits"),
    pl.col("sr_id").n_unique().alias("unique_srs_visited"),
    pl.col("sr_id").first().alias("primary_sr_id"),
    pl.col("visit_time").min().alias("first_visit_time"),
    pl.col("visit_time").max().alias("last_visit_time")
])

# Master Join
df_master = df_dept.join(outlet_sales, on="dept_id", how="left")
df_master = df_master.join(outlet_visits, on="dept_id", how="left")

df_master = df_master.with_columns([
    pl.col("total_revenue").fill_null(0.0),
    pl.col("total_orders").fill_null(0),
    pl.col("total_units").fill_null(0.0),
    pl.col("unique_skus").fill_null(0),
    pl.col("total_visits").fill_null(0),
    pl.col("unique_srs_visited").fill_null(0)
])

# Detailed Metrics
tot_reg = len(df_master)
tot_active = df_master.filter(pl.col("total_orders") > 0).height
tot_visited = df_master.filter(pl.col("total_visits") > 0).height
tot_unvisited = df_master.filter(pl.col("total_visits") == 0).height
visited_no_order = df_master.filter((pl.col("total_visits") > 0) & (pl.col("total_orders") == 0)).height
order_no_visit = df_master.filter((pl.col("total_visits") == 0) & (pl.col("total_orders") > 0)).height
tot_revenue = df_master.select(pl.col("total_revenue").sum()).item()
tot_orders = df_master.select(pl.col("total_orders").sum()).item()
tot_visits_count = df_master.select(pl.col("total_visits").sum()).item()

# Outlet Tiers
df_master = df_master.with_columns([
    pl.when(pl.col("total_revenue") >= 100000).then(pl.lit("Tier 1: Platinum (>100k)"))
      .when(pl.col("total_revenue") >= 30000).then(pl.lit("Tier 2: Gold (30k-100k)"))
      .when(pl.col("total_revenue") >= 10000).then(pl.lit("Tier 3: Silver (10k-30k)"))
      .when(pl.col("total_revenue") > 0).then(pl.lit("Tier 4: Bronze (<10k)"))
      .otherwise(pl.lit("Tier 5: Zero-Revenue / Dormant")).alias("outlet_tier")
])

tier_summary = df_master.group_by("outlet_tier").agg([
    pl.col("dept_id").count().alias("outlet_count"),
    pl.col("total_revenue").sum().alias("total_revenue"),
    pl.col("total_orders").sum().alias("total_orders"),
    pl.col("total_visits").sum().alias("total_visits")
]).sort("total_revenue", descending=True)

# Territory Analytics
territory_summary = df_master.group_by("territory_id").agg([
    pl.col("dept_id").count().alias("registered_outlets"),
    (pl.col("total_orders") > 0).sum().alias("active_outlets"),
    (pl.col("total_visits") > 0).sum().alias("visited_outlets"),
    (pl.col("total_visits") == 0).sum().alias("unvisited_outlets"),
    pl.col("total_visits").sum().alias("total_visits"),
    pl.col("total_orders").sum().alias("total_orders"),
    pl.col("total_revenue").sum().alias("total_revenue_bdt")
]).with_columns([
    (pl.col("active_outlets") / pl.col("registered_outlets") * 100).round(2).alias("activation_rate_pct"),
    (pl.col("visited_outlets") / pl.col("registered_outlets") * 100).round(2).alias("visit_coverage_pct"),
    (pl.col("total_revenue_bdt") / pl.col("active_outlets").clip(lower_bound=1)).round(2).alias("revenue_per_active_outlet")
]).sort("total_revenue_bdt", descending=True)

# Top 20 Territories
top_20_territories = territory_summary.head(20)

# Bottom Territories with High Registered but low revenue (Expansion / Underperforming)
underperforming_territories = territory_summary.filter(pl.col("registered_outlets") >= 50).sort("activation_rate_pct").head(20)

# High visit zero order outlets
high_visit_zero_order = df_master.filter((pl.col("total_visits") >= 4) & (pl.col("total_orders") == 0)).select([
    "dept_id", "outlet_name", "outlet_code", "territory_id", "total_visits", "address", "primary_sr_id"
]).sort("total_visits", descending=True).head(50)

# High density Micro-Hubs (Top 300)
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

# SR Route & Inefficiency Diagnostics
sr_journey = df_checkings.group_by(["sr_id"]).agg([
    pl.col("checking_id").count().alias("total_visits"),
    pl.col("dept_id").n_unique().alias("unique_outlets"),
    pl.col("checkin_distance").mean().alias("avg_checkin_distance_m"),
    pl.col("checkin_distance").quantile(0.9).alias("p90_checkin_distance_m")
]).sort("total_visits", descending=True)

# Save clean structured data for report
results = {
    "tot_reg": tot_reg,
    "tot_active": tot_active,
    "active_rate": round(tot_active / tot_reg * 100, 2),
    "tot_visited": tot_visited,
    "visit_rate": round(tot_visited / tot_reg * 100, 2),
    "tot_unvisited": tot_unvisited,
    "unvisited_rate": round(tot_unvisited / tot_reg * 100, 2),
    "visited_no_order": visited_no_order,
    "order_no_visit": order_no_visit,
    "tot_revenue_bdt": tot_revenue,
    "tot_revenue_crore": round(tot_revenue / 10000000, 2),
    "tot_orders": tot_orders,
    "tot_visits_count": tot_visits_count,
    "tier_summary": tier_summary.to_dicts(),
    "top_20_territories": top_20_territories.to_dicts(),
    "underperforming_territories": underperforming_territories.to_dicts(),
    "top_micro_hubs_sample": micro_hubs.head(20).to_dicts(),
    "high_visit_zero_order_sample": high_visit_zero_order.head(20).to_dicts(),
    "sr_journey_sample": sr_journey.head(20).to_dicts()
}

with open(r"E:\ITL FINAL ADV ANALYSIS\module1_metrics.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Module 1 Analytics JSON exported successfully!")
