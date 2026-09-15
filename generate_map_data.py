import polars as pl
import json
import math
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
print("--- Generating Interactive Geospatial Intelligence Map Data ---")

dept_path = r"E:\ITL FINAL ADV ANALYSIS\itl_dept.csv"
checkings_path = r"E:\ITL FINAL ADV ANALYSIS\itl_checkings.csv"
orders_path = r"E:\ITL FINAL ADV ANALYSIS\itl_orders.csv"

# Load Clean Orders
print("1. Aggregating Orders...")
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
    pl.col("order_id").n_unique().alias("total_orders")
])

# Load Clean Checkings
print("2. Aggregating Checkings & SR Tracking...")
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
    pl.col("created_at").alias("visit_time")
])

outlet_visits = df_checkings.group_by("dept_id").agg([
    pl.col("checking_id").count().alias("total_visits"),
    pl.col("sr_id").first().alias("sr_id")
])

# Load Outlet Master
print("3. Loading Master Outlets...")
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
    pl.col("address").alias("address")
])

# Master Join
print("4. Joining Geocoded Datasets...")
df_master = df_dept.join(outlet_sales, on="dept_id", how="left")
df_master = df_master.join(outlet_visits, on="dept_id", how="left")

df_master = df_master.with_columns([
    pl.col("total_revenue").fill_null(0.0),
    pl.col("total_orders").fill_null(0),
    pl.col("total_visits").fill_null(0)
])

# Filter valid Bangladesh coordinates (Lat: 20.5 to 26.8, Long: 88.0 to 92.8)
valid_outlets = df_master.filter(
    pl.col("lat").is_not_null() & pl.col("long").is_not_null() &
    (pl.col("lat") >= 20.5) & (pl.col("lat") <= 26.8) &
    (pl.col("long") >= 88.0) & (pl.col("long") <= 92.8)
)
print(f"Total Valid Geocoded Outlets: {len(valid_outlets):,}")

# Assign Tiers
valid_outlets = valid_outlets.with_columns([
    pl.when(pl.col("total_revenue") >= 100000).then(pl.lit("Tier 1 (Platinum >100k)"))
      .when(pl.col("total_revenue") >= 30000).then(pl.lit("Tier 2 (Gold 30k-100k)"))
      .when(pl.col("total_revenue") >= 10000).then(pl.lit("Tier 3 (Silver 10k-30k)"))
      .when(pl.col("total_revenue") > 0).then(pl.lit("Tier 4 (Bronze <10k)"))
      .otherwise(pl.lit("Tier 5 (Unsold / Dormant)")).alias("tier"),
    pl.when(pl.col("total_visits") == 0).then(pl.lit("Blind Spot (0 Visits)"))
      .when((pl.col("total_visits") >= 3) & (pl.col("total_orders") == 0)).then(pl.lit("Red Flag (High Visit, 0 Orders)"))
      .when(pl.col("total_orders") > 0).then(pl.lit("Active Ordering"))
      .otherwise(pl.lit("Visited Inactive")).alias("status_type")
])

# 1. Sample Clean Outlets across Tiers and Statuses for Map Visualization (Fast rendering in browser)
print("5. Sampling Outlets for Map...")
tier1 = valid_outlets.filter(pl.col("tier") == "Tier 1 (Platinum >100k)").head(3000)
tier2 = valid_outlets.filter(pl.col("tier") == "Tier 2 (Gold 30k-100k)").sample(n=min(3000, valid_outlets.filter(pl.col("tier") == "Tier 2 (Gold 30k-100k)").height), seed=42)
tier3 = valid_outlets.filter(pl.col("tier") == "Tier 3 (Silver 10k-30k)").sample(n=min(2000, valid_outlets.filter(pl.col("tier") == "Tier 3 (Silver 10k-30k)").height), seed=42)
blind_spots = valid_outlets.filter(pl.col("status_type") == "Blind Spot (0 Visits)").sample(n=min(3000, valid_outlets.filter(pl.col("status_type") == "Blind Spot (0 Visits)").height), seed=42)
red_flags = valid_outlets.filter(pl.col("status_type") == "Red Flag (High Visit, 0 Orders)").head(1500)

map_sample = pl.concat([tier1, tier2, tier3, blind_spots, red_flags]).unique(subset=["dept_id"])
print(f"Map Outlets Sample Count: {len(map_sample):,}")

# 2. Extract Top 300 Micro-Hubs (Density & Revenue)
micro_hubs = valid_outlets.with_columns([
    pl.col("lat").round(2).alias("lat_grid"),
    pl.col("long").round(2).alias("long_grid")
]).group_by(["lat_grid", "long_grid"]).agg([
    pl.col("dept_id").count().alias("outlet_count"),
    pl.col("total_revenue").sum().alias("hub_revenue"),
    pl.col("total_visits").sum().alias("hub_visits"),
    pl.col("total_orders").sum().alias("hub_orders")
]).sort("hub_revenue", descending=True).head(300)

# 3. Extract sample SR Route Paths (Journey Tracking)
top_sr = df_checkings.filter(
    pl.col("checkin_lat").is_not_null() & pl.col("checkin_long").is_not_null() &
    (pl.col("checkin_lat") >= 20.5) & (pl.col("checkin_lat") <= 26.8) &
    (pl.col("checkin_long") >= 88.0) & (pl.col("checkin_long") <= 92.8)
).group_by("sr_id").agg(pl.len().alias("count")).sort("count", descending=True).head(5)["sr_id"].to_list()

sr_routes = []
for sr in top_sr:
    sr_pts = df_checkings.filter(pl.col("sr_id") == sr).sort("visit_time").head(40).select([
        pl.col("checkin_lat").alias("lat"),
        pl.col("checkin_long").alias("lng"),
        pl.col("visit_time")
    ]).to_dicts()
    if len(sr_pts) >= 5:
        sr_routes.append({"sr_id": f"SR-{sr}", "points": sr_pts})

# Prepare Export Objects
map_data = {
    "outlets": map_sample.select([
        "dept_id", "outlet_name", "territory_id", "lat", "long", "total_revenue", "total_orders", "total_visits", "tier", "status_type"
    ]).to_dicts(),
    "micro_hubs": micro_hubs.to_dicts(),
    "sr_routes": sr_routes,
    "summary": {
        "total_master_outlets": len(df_master),
        "total_geocoded": len(valid_outlets),
        "total_revenue_bdt": df_master.select(pl.col("total_revenue").sum()).item(),
        "total_active": df_master.filter(pl.col("total_orders") > 0).height,
        "total_blind_spots": df_master.filter(pl.col("total_visits") == 0).height,
        "total_red_flags": df_master.filter((pl.col("total_visits") >= 3) & (pl.col("total_orders") == 0)).height
    }
}

with open(r"E:\ITL FINAL ADV ANALYSIS\map_data.json", "w", encoding="utf-8") as f:
    json.dump(map_data, f, ensure_ascii=False)

print("Map data JSON created successfully!")
