import polars as pl
import json
import math
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
print("--- Generating Dedicated 7-in-1 Geo-Intelligence Explorer Suite ---")

dept_path = r"E:\ITL FINAL ADV ANALYSIS\itl_dept.csv"
checkings_path = r"E:\ITL FINAL ADV ANALYSIS\itl_checkings.csv"
orders_path = r"E:\ITL FINAL ADV ANALYSIS\itl_orders.csv"

# 1. Clean Orders
print("Reading Orders...")
df_orders = pl.read_csv(
    orders_path,
    infer_schema_length=10000,
    ignore_errors=True,
    truncate_ragged_lines=True
).select([
    pl.col("order_id").cast(pl.Utf8),
    pl.col("order_date").cast(pl.Utf8),
    pl.col("buyer_department_id").cast(pl.Utf8).alias("dept_id"),
    pl.col("amount").cast(pl.Float64, strict=False).alias("amount"),
    pl.col("order_qty").cast(pl.Float64, strict=False).alias("order_qty"),
    pl.col("order_status").alias("order_status")
]).filter(
    (pl.col("order_qty") < 1000000) & 
    (pl.col("amount") < 5000000) &
    (pl.col("order_status").is_in(["accepted", "delivered"]))
)

outlet_sales = df_orders.group_by("dept_id").agg([
    pl.col("amount").sum().alias("total_revenue"),
    pl.col("order_id").n_unique().alias("total_orders"),
    pl.col("order_qty").sum().alias("total_units")
])

# 2. Checkings
print("Reading Checkings...")
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
    pl.col("created_at").alias("visit_time"),
    pl.col("checkin_distance").cast(pl.Float64, strict=False).alias("checkin_distance")
])

outlet_visits = df_checkings.group_by("dept_id").agg([
    pl.col("checking_id").count().alias("total_visits"),
    pl.col("sr_id").first().alias("sr_id")
])

# 3. Dept Master
print("Reading Dept Master...")
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
    pl.col("lat").cast(pl.Float64, strict=False).alias("lat"),
    pl.col("long").cast(pl.Float64, strict=False).alias("long"),
    pl.col("address").alias("address"),
    pl.col("status").alias("status")
])

# Merge
df_master = df_dept.join(outlet_sales, on="dept_id", how="left")
df_master = df_master.join(outlet_visits, on="dept_id", how="left")

df_master = df_master.with_columns([
    pl.col("total_revenue").fill_null(0.0),
    pl.col("total_orders").fill_null(0),
    pl.col("total_visits").fill_null(0)
])

# Valid geocoded outlets
valid_outlets = df_master.filter(
    pl.col("lat").is_not_null() & pl.col("long").is_not_null() &
    (pl.col("lat") >= 20.5) & (pl.col("lat") <= 26.8) &
    (pl.col("long") >= 88.0) & (pl.col("long") <= 92.8)
)

print(f"Total Geocoded Outlets: {len(valid_outlets):,}")

# Classify Items for 7 Distinct Views
valid_outlets = valid_outlets.with_columns([
    # Tier classification
    pl.when(pl.col("total_revenue") >= 100000).then(pl.lit("Tier 1: Platinum (>100k)"))
      .when(pl.col("total_revenue") >= 30000).then(pl.lit("Tier 2: Gold (30k-100k)"))
      .when(pl.col("total_revenue") >= 10000).then(pl.lit("Tier 3: Silver (10k-30k)"))
      .when(pl.col("total_revenue") > 0).then(pl.lit("Tier 4: Bronze (<10k)"))
      .otherwise(pl.lit("Tier 5: Dormant / Zero Rev")).alias("tier"),
    # Footprint classification
    pl.when(pl.col("total_orders") > 0).then(pl.lit("Active Store (Ordered)"))
      .otherwise(pl.lit("Registered Only (Unsold)")).alias("footprint_status"),
    # Blind Spot classification
    pl.when(pl.col("total_visits") == 0).then(pl.lit("Operational Blind Spot (0 Visits)"))
      .when((pl.col("total_visits") >= 3) & (pl.col("total_orders") == 0)).then(pl.lit("High-Visit Zero-Order Red Flag"))
      .otherwise(pl.lit("Normal Active")).alias("audit_status")
])

# 1. Registered vs Active Stores (Sample for fast nationwide rendering)
active_sample = valid_outlets.filter(pl.col("footprint_status") == "Active Store (Ordered)").sample(n=5000, seed=1)
registered_only_sample = valid_outlets.filter(pl.col("footprint_status") == "Registered Only (Unsold)").sample(n=4000, seed=2)
footprint_data = pl.concat([active_sample, registered_only_sample]).select([
    "dept_id", "outlet_name", "territory_id", "lat", "long", "footprint_status", "total_revenue", "total_orders"
]).to_dicts()

# 2. Heatmap Points (Visits intensity)
heat_points = valid_outlets.filter(pl.col("total_visits") > 0).select(["lat", "long", "total_visits"]).sample(n=10000, seed=3).to_dicts()

# 3. Top 300 Micro-Hubs
micro_hubs = valid_outlets.with_columns([
    pl.col("lat").round(2).alias("lat_grid"),
    pl.col("long").round(2).alias("long_grid")
]).group_by(["lat_grid", "long_grid"]).agg([
    pl.col("dept_id").count().alias("outlet_count"),
    pl.col("total_revenue").sum().alias("hub_revenue"),
    pl.col("total_visits").sum().alias("hub_visits"),
    pl.col("total_orders").sum().alias("hub_orders")
]).sort("hub_revenue", descending=True).head(300).to_dicts()

# 4. Blind Spots (Unvisited Outlets)
blind_spots_data = valid_outlets.filter(pl.col("audit_status") == "Operational Blind Spot (0 Visits)").sample(n=4000, seed=4).select([
    "dept_id", "outlet_name", "territory_id", "lat", "long", "address"
]).to_dicts()

# 5. White Space Expansion Opportunities (Clusters with high unvisited/dormant ratio but nearby active demand)
white_space_data = valid_outlets.with_columns([
    pl.col("lat").round(1).alias("lat_region"),
    pl.col("long").round(1).alias("long_region")
]).group_by(["lat_region", "long_region"]).agg([
    pl.col("dept_id").count().alias("total_regional_stores"),
    (pl.col("total_orders") > 0).sum().alias("active_stores"),
    (pl.col("total_visits") == 0).sum().alias("unvisited_stores"),
    pl.col("total_revenue").sum().alias("regional_revenue")
]).filter(pl.col("total_regional_stores") >= 100).with_columns([
    ((pl.col("unvisited_stores") / pl.col("total_regional_stores")) * 100).round(1).alias("unvisited_pct")
]).sort("unvisited_pct", descending=True).head(50).to_dicts()

# 6. 3D Sales Height Outlets (Top High-Revenue Pillars)
pillars_3d_data = valid_outlets.filter(pl.col("total_revenue") > 50000).sort("total_revenue", descending=True).head(2000).select([
    "dept_id", "outlet_name", "territory_id", "lat", "long", "total_revenue", "total_orders", "tier"
]).to_dicts()

# 7. High-Value Non-Ordered Outlets (Route Flaws)
high_visit_zero_order_data = valid_outlets.filter(pl.col("audit_status") == "High-Visit Zero-Order Red Flag").sort("total_visits", descending=True).head(1000).select([
    "dept_id", "outlet_name", "territory_id", "lat", "long", "total_visits", "address", "sr_id"
]).to_dicts()

# 8. SR Movement & Journey Routes (Multi-SR Tracking)
top_srs = [18, 42, 32, 904, 887, 111, 725, 396]
sr_routes_data = []
for sr in top_srs:
    pts = df_checkings.filter(
        (pl.col("sr_id") == str(sr)) &
        pl.col("checkin_lat").is_not_null() & (pl.col("checkin_lat") >= 20.5) & (pl.col("checkin_lat") <= 26.8) &
        pl.col("checkin_long").is_not_null() & (pl.col("checkin_long") >= 88.0) & (pl.col("checkin_long") <= 92.8)
    ).sort("visit_time").head(50).select([
        pl.col("checkin_lat").alias("lat"),
        pl.col("checkin_long").alias("lng"),
        pl.col("visit_time"),
        pl.col("checkin_distance")
    ]).to_dicts()
    if len(pts) >= 5:
        sr_routes_data.append({
            "sr_id": f"SR #{sr}",
            "waypoints": len(pts),
            "points": pts
        })

full_suite_data = {
    "footprint": footprint_data,
    "heat_points": heat_points,
    "micro_hubs": micro_hubs,
    "blind_spots": blind_spots_data,
    "white_space": white_space_data,
    "pillars_3d": pillars_3d_data,
    "high_visit_zero_order": high_visit_zero_order_data,
    "sr_routes": sr_routes_data,
    "stats": {
        "total_stores": len(df_master),
        "active_stores": df_master.filter(pl.col("total_orders") > 0).height,
        "blind_spots": df_master.filter(pl.col("total_visits") == 0).height,
        "red_flags": df_master.filter((pl.col("total_visits") >= 3) & (pl.col("total_orders") == 0)).height,
        "revenue_bdt": df_master.select(pl.col("total_revenue").sum()).item()
    }
}

with open(r"E:\ITL FINAL ADV ANALYSIS\module1_full_suite_data.json", "w", encoding="utf-8") as f:
    json.dump(full_suite_data, f, ensure_ascii=False)

print("Full Module 1 Map Data Exported Successfully!")
