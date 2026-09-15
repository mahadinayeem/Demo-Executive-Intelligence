import polars as pl
import json
import math
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
print("--- Generating Division-Wise Hierarchical Map Dataset with Drill-down Filters ---")

dept_path = r"E:\ITL FINAL ADV ANALYSIS\itl_dept.csv"
checkings_path = r"E:\ITL FINAL ADV ANALYSIS\itl_checkings.csv"
orders_path = r"E:\ITL FINAL ADV ANALYSIS\itl_orders.csv"

# 1. Clean Orders
print("1. Reading Orders...")
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
print("2. Reading Checkings...")
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

# 3. Dept Master
print("3. Reading Dept Master...")
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

# Merge
df_master = df_dept.join(outlet_sales, on="dept_id", how="left")
df_master = df_master.join(outlet_visits, on="dept_id", how="left")

df_master = df_master.with_columns([
    pl.col("total_revenue").fill_null(0.0),
    pl.col("total_orders").fill_null(0),
    pl.col("total_visits").fill_null(0)
])

# Filter valid Bangladesh coordinates
valid_outlets = df_master.filter(
    pl.col("lat").is_not_null() & pl.col("long").is_not_null() &
    (pl.col("lat") >= 20.5) & (pl.col("lat") <= 26.8) &
    (pl.col("long") >= 88.0) & (pl.col("long") <= 92.8)
)

print(f"Total Geocoded Outlets: {len(valid_outlets):,}")

# Assign Division based on GPS Bounding Boxes / Geolocation
# Dhaka Metro: Lat 23.65 to 23.95, Long 90.30 to 90.55
# Dhaka Division (Other): Lat 23.2 to 24.3, Long 89.8 to 91.0
# Chattogram: Lat 20.5 to 23.3, Long 91.2 to 92.8
# Rajshahi: Lat 24.0 to 25.2, Long 88.0 to 89.8
# Rangpur: Lat 25.2 to 26.8, Long 88.0 to 89.8
# Sylhet: Lat 23.9 to 25.3, Long 91.2 to 92.6
# Khulna: Lat 21.5 to 24.0, Long 88.8 to 89.9
# Barishal: Lat 21.8 to 23.1, Long 89.9 to 90.9
# Mymensingh: Lat 24.3 to 25.3, Long 89.8 to 91.0

valid_outlets = valid_outlets.with_columns([
    pl.when((pl.col("lat") >= 23.65) & (pl.col("lat") <= 23.95) & (pl.col("long") >= 90.30) & (pl.col("long") <= 90.55))
      .then(pl.lit("Dhaka Metro"))
      .when((pl.col("lat") >= 25.2) & (pl.col("long") <= 89.8))
      .then(pl.lit("Rangpur"))
      .when((pl.col("lat") >= 24.0) & (pl.col("lat") < 25.2) & (pl.col("long") <= 89.8))
      .then(pl.lit("Rajshahi"))
      .when((pl.col("long") >= 91.4) & (pl.col("lat") >= 23.9))
      .then(pl.lit("Sylhet"))
      .when((pl.col("lat") >= 24.3) & (pl.col("lat") <= 25.3) & (pl.col("long") >= 89.8) & (pl.col("long") < 91.4))
      .then(pl.lit("Mymensingh"))
      .when((pl.col("lat") <= 23.3) & (pl.col("long") >= 91.0))
      .then(pl.lit("Chattogram"))
      .when((pl.col("lat") <= 23.1) & (pl.col("long") >= 89.9) & (pl.col("long") < 91.0))
      .then(pl.lit("Barishal"))
      .when((pl.col("lat") <= 24.0) & (pl.col("long") >= 88.8) & (pl.col("long") < 89.9))
      .then(pl.lit("Khulna"))
      .otherwise(pl.lit("Dhaka Region")).alias("division")
])

# Status & Tier
valid_outlets = valid_outlets.with_columns([
    pl.when(pl.col("total_orders") > 0).then(pl.lit("Active Store (Ordered)")).otherwise(pl.lit("Registered Only (Unsold)")).alias("footprint_status"),
    pl.when(pl.col("total_visits") == 0).then(pl.lit("Operational Blind Spot (0 Visits)"))
      .when((pl.col("total_visits") >= 3) & (pl.col("total_orders") == 0)).then(pl.lit("High-Visit Zero-Order Red Flag"))
      .otherwise(pl.lit("Normal Active")).alias("audit_status"),
    pl.when(pl.col("total_revenue") >= 100000).then(pl.lit("Tier 1: Platinum (>100k)"))
      .when(pl.col("total_revenue") >= 30000).then(pl.lit("Tier 2: Gold (30k-100k)"))
      .when(pl.col("total_revenue") >= 10000).then(pl.lit("Tier 3: Silver (10k-30k)"))
      .when(pl.col("total_revenue") > 0).then(pl.lit("Tier 4: Bronze (<10k)"))
      .otherwise(pl.lit("Tier 5: Dormant / Zero Rev")).alias("tier")
])

# Distribution count per division
div_counts = valid_outlets.group_by("division").agg([
    pl.len().alias("total_stores"),
    (pl.col("total_orders") > 0).sum().alias("active_stores"),
    (pl.col("total_visits") == 0).sum().alias("blind_spots"),
    pl.col("total_revenue").sum().alias("total_revenue")
]).sort("total_stores", descending=True)

print("Division breakdown:")
print(div_counts)

# Sample by division so every division has dedicated rich data (Up to 1,500 stores per division for fast crisp filtering)
divisions = valid_outlets["division"].unique().to_list()
sampled_dfs = []
for div in divisions:
    sub = valid_outlets.filter(pl.col("division") == div)
    # Take sample if larger than 1500
    if len(sub) > 1500:
        sampled_dfs.append(sub.sample(n=1500, seed=42))
    else:
        sampled_dfs.append(sub)

final_outlets = pl.concat(sampled_dfs)
print(f"Final Exported Filterable Outlets: {len(final_outlets):,}")

# Prepare Clean Sanitized Objects
def clean_str(val):
    if val is None:
        return ""
    return str(val).replace('"', ' ').replace("'", " ").replace('\n', ' ').replace('\r', ' ').replace('\\', ' ')

outlets_list = []
for row in final_outlets.to_dicts():
    outlets_list.append({
        "dept_id": str(row["dept_id"]),
        "name": clean_str(row["outlet_name"]),
        "territory_id": str(row["territory_id"]),
        "division": row["division"],
        "lat": round(float(row["lat"]), 6),
        "long": round(float(row["long"]), 6),
        "revenue": round(float(row["total_revenue"]), 2),
        "orders": int(row["total_orders"]),
        "visits": int(row["total_visits"]),
        "tier": row["tier"],
        "status": row["footprint_status"],
        "audit": row["audit_status"],
        "address": clean_str(row["address"])
    })

# Division Stats for KPI Ribbon
div_stats = {}
for row in div_counts.to_dicts():
    div_stats[row["division"]] = {
        "total_stores": int(row["total_stores"]),
        "active_stores": int(row["active_stores"]),
        "active_pct": round(row["active_stores"] / row["total_stores"] * 100, 1),
        "blind_spots": int(row["blind_spots"]),
        "blind_pct": round(row["blind_spots"] / row["total_stores"] * 100, 1),
        "total_revenue": round(row["total_revenue"], 2),
        "rev_crore": round(row["total_revenue"] / 10000000, 2)
    }

# Top 300 Micro-Hubs with Division tag
micro_hubs = valid_outlets.with_columns([
    pl.col("lat").round(2).alias("lat_grid"),
    pl.col("long").round(2).alias("long_grid")
]).group_by(["lat_grid", "long_grid", "division"]).agg([
    pl.col("dept_id").count().alias("outlet_count"),
    pl.col("total_revenue").sum().alias("hub_revenue"),
    pl.col("total_visits").sum().alias("hub_visits"),
    pl.col("total_orders").sum().alias("hub_orders")
]).sort("hub_revenue", descending=True).head(300)

hubs_list = []
for row in micro_hubs.to_dicts():
    hubs_list.append({
        "lat": row["lat_grid"],
        "lng": row["long_grid"],
        "division": row["division"],
        "count": row["outlet_count"],
        "revenue": round(row["hub_revenue"], 2),
        "visits": row["hub_visits"]
    })

# Write to map_suite_data.js
js_content = "const MAP_DATA = {\n"
js_content += f'  "divisions": {json.dumps(div_stats, ensure_ascii=False)},\n'
js_content += f'  "outlets": {json.dumps(outlets_list, ensure_ascii=False)},\n'
js_content += f'  "micro_hubs": {json.dumps(hubs_list, ensure_ascii=False)}\n'
js_content += "};\n"

with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("Division-wise data successfully saved in map_suite_data.js!")
