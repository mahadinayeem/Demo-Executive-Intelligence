import polars as pl
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
print("--- Generating Full 281k Outlets Vector Grid Dataset ---")

dept_path = r"E:\ITL FINAL ADV ANALYSIS\itl_dept.csv"
checkings_path = r"E:\ITL FINAL ADV ANALYSIS\itl_checkings.csv"
orders_path = r"E:\ITL FINAL ADV ANALYSIS\itl_orders.csv"

# 1. Orders
print("Reading Orders...")
df_orders = pl.read_csv(
    orders_path,
    infer_schema_length=10000,
    ignore_errors=True,
    truncate_ragged_lines=True
).select([
    pl.col("order_id").cast(pl.Utf8),
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
    pl.col("user_id").cast(pl.Utf8).alias("sr_id")
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
    pl.col("address").alias("address")
])

# Join all
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

print(f"Total Geocoded Outlets in Database: {len(valid_outlets):,}")

# Assign Division
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

# Status
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

# Summary per division
div_counts = valid_outlets.group_by("division").agg([
    pl.len().alias("total_stores"),
    (pl.col("total_orders") > 0).sum().alias("active_stores"),
    (pl.col("total_visits") == 0).sum().alias("blind_spots"),
    pl.col("total_revenue").sum().alias("total_revenue")
]).sort("total_stores", descending=True)

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

# 1. Precise Micro-Grid Clustered points covering ALL 281,337 stores (0.01 degree grid ~ 1km exact clustering)
# This perfectly represents all 281,337 stores without crashing Leaflet/Browser memory!
print("Building Full 281k Aggregate Micro-Clusters...")
grid_all = valid_outlets.with_columns([
    pl.col("lat").round(2).alias("lat_g"),
    pl.col("long").round(2).alias("long_g")
]).group_by(["lat_g", "long_g", "division"]).agg([
    pl.len().alias("total_stores"),
    (pl.col("total_orders") > 0).sum().alias("active_stores"),
    (pl.col("total_visits") == 0).sum().alias("blind_spots"),
    (pl.col("total_visits") >= 3).and_(pl.col("total_orders") == 0).sum().alias("red_flags"),
    (pl.col("total_revenue") >= 100000).sum().alias("tier1_stores"),
    (pl.col("total_revenue") >= 30000).and_(pl.col("total_revenue") < 100000).sum().alias("tier2_stores"),
    pl.col("total_revenue").sum().alias("grid_revenue"),
    pl.col("total_visits").sum().alias("grid_visits"),
    pl.col("total_orders").sum().alias("grid_orders")
])

print(f"Total High-Precision Clusters: {len(grid_all):,}")
print(f"Sum of stores across clusters: {grid_all.select(pl.col('total_stores').sum()).item():,}")

grid_list = []
for row in grid_all.to_dicts():
    grid_list.append({
        "lat": row["lat_g"],
        "lng": row["long_g"],
        "division": row["division"],
        "total": row["total_stores"],
        "active": row["active_stores"],
        "unsold": row["total_stores"] - row["active_stores"],
        "blind": row["blind_spots"],
        "red_flag": row["red_flags"],
        "t1": row["tier1_stores"],
        "t2": row["tier2_stores"],
        "revenue": round(row["grid_revenue"], 2),
        "visits": row["grid_visits"],
        "orders": row["grid_orders"]
    })

# Also take top 10,000 individual mega stores for street-level individual pin inspection
individual_pins = valid_outlets.sort("total_revenue", descending=True).head(10000).select([
    "dept_id", "outlet_name", "territory_id", "division", "lat", "long", "total_revenue", "total_orders", "total_visits", "tier", "footprint_status", "audit_status"
]).to_dicts()

clean_pins = []
for p in individual_pins:
    clean_pins.append({
        "id": str(p["dept_id"]),
        "name": str(p["outlet_name"] or "").replace('"', ' ').replace("'", " "),
        "t_id": str(p["territory_id"]),
        "div": p["division"],
        "lat": round(p["lat"], 5),
        "lng": round(p["long"], 5),
        "rev": round(p["total_revenue"], 2),
        "orders": p["total_orders"],
        "visits": p["total_visits"],
        "tier": p["tier"],
        "status": p["footprint_status"],
        "audit": p["audit_status"]
    })

# Export to map_suite_data.js
js_content = "const MAP_DATA = {\n"
js_content += f'  "total_universe": {len(valid_outlets)},\n'
js_content += f'  "divisions": {json.dumps(div_stats, ensure_ascii=False)},\n'
js_content += f'  "grid_all": {json.dumps(grid_list, ensure_ascii=False)},\n'
js_content += f'  "individual_pins": {json.dumps(clean_pins, ensure_ascii=False)}\n'
js_content += "};\n"

with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("map_suite_data.js updated with 100% full 281,337 store aggregates and top individual pins!")
