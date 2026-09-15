import polars as pl
import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
print("--- Updating 281k Dataset with Precise Division Classifications & Physical Addresses ---")

dept_path = r"E:\ITL FINAL ADV ANALYSIS\itl_dept.csv"
checkings_path = r"E:\ITL FINAL ADV ANALYSIS\itl_checkings.csv"
orders_path = r"E:\ITL FINAL ADV ANALYSIS\itl_orders.csv"
boundary_path = r"E:\ITL FINAL ADV ANALYSIS\bd_boundary.json"

# 1. Orders
print("1. Reading Orders...")
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
print("2. Reading Checkings...")
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

# Join all
print("4. Joining Master Dataset...")
df_master = df_dept.join(outlet_sales, on="dept_id", how="left")
df_master = df_master.join(outlet_visits, on="dept_id", how="left")

df_master = df_master.with_columns([
    pl.col("total_revenue").fill_null(0.0),
    pl.col("total_orders").fill_null(0),
    pl.col("total_visits").fill_null(0),
    pl.col("address").fill_null("Local Market Area")
])

# Valid geocoded outlets
valid_outlets = df_master.filter(
    pl.col("lat").is_not_null() & pl.col("long").is_not_null() &
    (pl.col("lat") >= 20.5) & (pl.col("lat") <= 26.8) &
    (pl.col("long") >= 88.0) & (pl.col("long") <= 92.8)
)

print(f"Total Geocoded Outlets: {len(valid_outlets):,}")

# Accurate Division Categorizer
keywords = [
    # Khulna Division (10 Districts)
    (r'(khulna|jessore|jashore|satkhira|bagerhat|kushtia|chuadanga|meherpur|jhenaidah|magura|narail|monirampur|keshabpur|benapole|অভয়নগর|খুলনা|যশোর|সাতক্ষীরা|বাগেরহাট|কুষ্টিয়া|চুয়াডাঙ্গা|মেহেরপুর|ঝিনাইদহ|মাগুরা|নড়াইল)', 'Khulna'),
    # Barishal Division (6 Districts)
    (r'(barishal|barisal|bhola|jhalokati|jhalakati|pirojpur|barguna|patuakhali|kuakata|চরফ্যাশন|বরিশাল|ভোলা|ঝালকাঠি|পিরোজপুর|বরগুনা|পটুয়াখালী)', 'Barishal'),
    # Rajshahi Division (8 Districts)
    (r'(rajshahi|bogura|bogra|pabna|sirajganj|naogaon|natore|nator|chapainawabganj|joypurhat|ishwardi|santahar|রাজশাহী|বগুড়া|পাবনা|সিরাজগঞ্জ|নওগাঁ|নাটোর|চাঁপাইনবাবগঞ্জ|জয়পুরহাট)', 'Rajshahi'),
    # Rangpur Division (8 Districts)
    (r'(rangpur|dinajpur|gaibandha|kurigram|lalmonirhat|nilphamari|panchagarh|thakurgaon|saidpur|রংপুর|দিনাজপুর|গাইবান্ধা|কুড়িগ্রাম|লালমনিরহাট|নীলফামারী|পঞ্চগড়|ঠাকুরগাঁও)', 'Rangpur'),
    # Sylhet Division (4 Districts)
    (r'(sylhet|moulvibazar|moulvibazar|habiganj|sunamganj|sreemangal|srimangal|beanibazar|সিলেট|মৌলভীবাজার|হবিগঞ্জ|সুনামগঞ্জ|শ্রীমঙ্গল)', 'Sylhet'),
    # Mymensingh Division (4 Districts)
    (r'(mymensingh|jamalpur|netrokona|sherpur|muktagacha|ভালুকা|ময়মনসিংহ|জামালপুর|নেত্রকোণা|শেরপুর)', 'Mymensingh'),
    # Chattogram Division (11 Districts)
    (r'(chattogram|chittagong|cox|cumilla|comilla|feni|brahmanbaria|noakhali|lakshmipur|chandpur|rangamati|bandarban|khagrachhari|agrabad|halishahar|chawkbazar|hathazari|sitakunda|mirsharai|teknaf|চট্টগ্রাম|কক্সবাজার|কুমিল্লা|ফেনী|ব্রাহ্মণবাড়িয়া|নোয়াখালী|লক্ষ্মীপুর|চাঁদপুর|রাঙ্গামাটি|বান্দরবান|খাগড়াছড়ি|আগ্রাবাদ|হালিশহর)', 'Chattogram'),
    # Dhaka Metro
    (r'(uttara|mirpur|gulshan|banani|dhanmondi|motijheel|mohammadpur|badda|khilkhet|rampura|tejgaon|jatrabari|lalbagh|dhanmondi|wari|shahbagh|paltan|shyamoli|মিরপুর|উত্তরা|গুলশান|ধানমন্ডি|মতিঝিল|মোহাম্মদপুর|বাড্ডা)', 'Dhaka Metro'),
    # Dhaka Region (Rest of Dhaka Division)
    (r'(gazipur|narayanganj|narsingdi|manikganj|munshiganj|tangail|kishoreganj|faridpur|madaripur|gopalganj|shariatpur|rajbari|savar|keraniganj|tongi|sreepur|সাভার|কেরানীগঞ্জ|টঙ্গী|গাজীপুর|নারায়ণগঞ্জ|নরসিংদী|মানিকগঞ্জ|মুন্সীগঞ্জ|টাঙ্গাইল|কিশোরগঞ্জ|ফরিদপুর|মাদারীপুর|গোপালগঞ্জ|শরীয়তপুর|রাজবাড়ী)', 'Dhaka Region')
]

compiled_regex = [(re.compile(p, re.IGNORECASE), div) for p, div in keywords]

def classify_outlet(addr, lat, lng):
    addr_str = str(addr or "").lower()
    for regex, div in compiled_regex:
        if regex.search(addr_str):
            return div
    
    # Precise Geometric Boundaries
    if 23.68 <= lat <= 23.90 and 90.33 <= lng <= 90.47:
        return 'Dhaka Metro'
    elif lat >= 25.15 and lng <= 89.85:
        return 'Rangpur'
    elif 23.80 <= lat < 25.15 and lng <= 89.80:
        return 'Rajshahi'
    elif lng >= 91.10 and lat >= 23.85:
        return 'Sylhet'
    elif 24.30 <= lat <= 25.40 and 89.70 <= lng < 91.10:
        return 'Mymensingh'
    elif lat <= 23.35 and lng >= 90.80:
        return 'Chattogram'
    elif lat <= 23.10 and 89.80 <= lng < 90.80:
        return 'Barishal'
    elif lat <= 24.30 and lng < 89.80:
        return 'Khulna'
    elif lat > 23.80 and lng >= 90.60:
        return 'Dhaka Region'
    else:
        return 'Dhaka Region'

print("5. Classifying Divisions...")
divisions_list = [classify_outlet(a, lt, lg) for a, lt, lg in zip(valid_outlets["address"], valid_outlets["lat"], valid_outlets["long"])]
valid_outlets = valid_outlets.with_columns(pl.Series("division", divisions_list))

# Division summary stats
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

print("Division breakdown:")
for k, v in div_stats.items():
    print(f" - {k}: {v['total_stores']:,} stores ({v['active_pct']}% active, BDT {v['rev_crore']} Cr)")

# Micro-Grid aggregation (0.01 deg grid ~ 1km)
valid_sorted = valid_outlets.sort("total_revenue", descending=True)

print("6. Generating Micro-Clusters with Addresses...")
grid_all = valid_sorted.with_columns([
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
    pl.col("total_orders").sum().alias("grid_orders"),
    pl.col("address").filter(pl.col("address").is_not_null() & (pl.col("address") != "") & (pl.col("address") != "Local Market Area")).first().alias("cluster_address"),
    pl.col("outlet_name").filter(pl.col("outlet_name").is_not_null() & (pl.col("outlet_name") != "")).head(2).alias("sample_names")
])

def clean_text(s):
    if not s:
        return ""
    cleaned = str(s).replace('"', ' ').replace("'", " ").replace('\n', ' ').replace('\r', ' ').strip()
    return cleaned

grid_list = []
for row in grid_all.to_dicts():
    addr = clean_text(row.get("cluster_address") or "")
    if not addr or addr.lower() == "none" or addr == "Local Market Area":
        addr = f"{row['division']} Market Area"
    
    samples = row.get("sample_names") or []
    sample_str = ", ".join([clean_text(name) for name in samples if name and str(name).lower() != "none"][:2])
    
    grid_list.append({
        "lat": row["lat_g"],
        "lng": row["long_g"],
        "division": row["division"],
        "address": addr,
        "stores_sample": sample_str,
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

print(f"Total Clusters Generated: {len(grid_list):,}")

# Read BD Boundary
with open(boundary_path, "r", encoding="utf-8") as f:
    bd_boundary = json.load(f)

# Total summary
total_universe = len(valid_outlets)
active_universe = int(valid_outlets.filter(pl.col("total_orders") > 0).shape[0])
blind_universe = int(valid_outlets.filter(pl.col("total_visits") == 0).shape[0])
total_revenue = round(float(valid_outlets.select(pl.col("total_revenue").sum()).item()), 2)
total_rev_crore = round(total_revenue / 10000000, 2)

map_data_obj = {
    "total_universe": total_universe,
    "active_universe": active_universe,
    "blind_universe": blind_universe,
    "total_rev_crore": total_rev_crore,
    "divisions": div_stats,
    "bd_boundary": bd_boundary,
    "grid_all": grid_list
}

js_content = "const MAP_DATA = " + json.dumps(map_data_obj, ensure_ascii=False) + ";\n"

with open(r"E:\ITL FINAL ADV ANALYSIS\map_suite_data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

with open(r"E:\ITL FINAL ADV ANALYSIS\map_hierarchy_data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("SUCCESS: map_suite_data.js & map_hierarchy_data.js updated!")
