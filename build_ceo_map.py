"""
CEO National Outlet Intelligence Map — Data Pipeline
Generates all JS data files for the CEO dashboard.
"""
import csv, json, sys, os, math
from collections import defaultdict
from datetime import datetime, timedelta

# Increase CSV field size limit for large fields
csv.field_size_limit(min(2147483647, sys.maxsize))

sys.stdout.reconfigure(encoding='utf-8')
print("=" * 60)
print("CEO OUTLET INTELLIGENCE — DATA PIPELINE")
print("=" * 60)

# ─── DIVISION KEYWORD MAPPING ─────────────────────────────────────
DHAKA_DISTRICTS    = {'dhaka','gazipur','narayanganj','manikganj','munshiganj','rajbari','madaripur','shariatpur','faridpur','tangail','kishoreganj','narsingdi','gopalganj'}
CHATT_DISTRICTS    = {'chittagong','chattogram','comilla','cumilla','cox','noakhali','feni','chandpur','lakshmipur','brahmanbaria','rangamati','khagrachhari','bandarban'}
RAJSHAHI_DISTRICTS = {'rajshahi','chapai','nawabganj','chapainawabganj','natore','sirajganj','pabna','bogura','bogra','joypurhat','naogaon'}
KHULNA_DISTRICTS   = {'khulna','bagerhat','satkhira','jessore','jashore','narail','magura','jhenaidah','jhenaidha','chuadanga','meherpur','kushtia'}
BARISHAL_DISTRICTS = {'barisal','barishal','bhola','patuakhali','pirojpur','jhalokati','barguna','perojpur'}
SYLHET_DISTRICTS   = {'sylhet','moulvibazar','maulvibazar','habiganj','sunamganj'}
RANGPUR_DISTRICTS  = {'rangpur','dinajpur','thakurgaon','panchagarh','nilphamari','lalmonirhat','kurigram','gaibandha'}
MYMEN_DISTRICTS    = {'mymensingh','jamalpur','sherpur','netrokona','netrakona'}

DIV_MAP = [
    ('Dhaka',      DHAKA_DISTRICTS,    0),
    ('Chattogram', CHATT_DISTRICTS,    1),
    ('Rajshahi',   RAJSHAHI_DISTRICTS, 2),
    ('Khulna',     KHULNA_DISTRICTS,   3),
    ('Barishal',   BARISHAL_DISTRICTS, 4),
    ('Sylhet',     SYLHET_DISTRICTS,   5),
    ('Rangpur',    RANGPUR_DISTRICTS,  6),
    ('Mymensingh', MYMEN_DISTRICTS,    7),
]

# Bangladesh geographic bounds per division for coordinate-based fallback
DIV_GEO_BOUNDS = {
    'Dhaka':      (23.2, 24.7, 89.7, 91.0),
    'Chattogram': (21.3, 23.8, 91.2, 92.7),
    'Rajshahi':   (24.0, 25.3, 88.0, 89.5),
    'Khulna':     (21.7, 23.9, 88.7, 90.0),
    'Barishal':   (21.7, 23.3, 89.7, 91.2),
    'Sylhet':     (24.0, 25.3, 91.0, 92.6),
    'Rangpur':    (25.0, 26.6, 88.5, 90.0),
    'Mymensingh': (24.3, 25.3, 89.7, 91.2),
}

DISTRICT_DIV = {}
for div_name, dset, idx in DIV_MAP:
    for d in dset:
        DISTRICT_DIV[d] = (div_name, idx)

def classify_division(territory_name, lat=None, lng=None):
    if territory_name:
        tl = territory_name.lower()
        for div_name, dset, idx in DIV_MAP:
            for kw in dset:
                if kw in tl:
                    return div_name, idx
        if 'dhaka' in tl: return 'Dhaka', 0
        if 'chatt' in tl or 'ctg' in tl: return 'Chattogram', 1
    # Fallback: use lat/lng bounds
    if lat and lng:
        try:
            flat, flng = float(lat), float(lng)
            for div_name, (lat_min, lat_max, lng_min, lng_max) in DIV_GEO_BOUNDS.items():
                if lat_min <= flat <= lat_max and lng_min <= flng <= lng_max:
                    return div_name, next(idx for n,_,idx in DIV_MAP if n == div_name)
        except:
            pass
    return 'Dhaka', 0

def extract_district(territory_name):
    if not territory_name:
        return 'Unknown'
    tl = territory_name.lower()
    for div_name, dset, idx in DIV_MAP:
        for kw in dset:
            if kw in tl:
                # Return properly capitalized district name
                return kw.title()
    # Return the first meaningful word
    parts = territory_name.split()
    for p in parts:
        if len(p) > 3:
            return p.title()
    return territory_name[:20]

# ─── STEP 1: LOAD DEPT MASTER ────────────────────────────────────
print("\n[1/5] Loading department master...")
dept_master = {}  # dept_id -> {name, code, lat, lng, territory_id, address}

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_dept.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        did = r.get('id', '')
        if not did:
            continue
        lat = r.get('lat', '') or ''
        lng = r.get('long', '') or ''
        dept_master[did] = {
            'name': r.get('name', ''),
            'code': r.get('code', ''),
            'lat': lat,
            'lng': lng,
            'territory_id': r.get('territory_id', ''),
            'address': r.get('address', '') or r.get('check_in_address', ''),
            'dept_type': r.get('department_type_id', ''),
            'status': r.get('status', 'active')
        }

print(f"   Loaded {len(dept_master):,} departments")

# ─── STEP 2: DETERMINE 4-MONTH WINDOW FROM CHECKINGS ────────────
print("\n[2/5] Determining 4-month analysis window...")

# Quick scan to find latest date
latest_date = None
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        ca = r.get('created_at') or ''
        d = ca[:10]
        if d and d > '2020-01-01':
            if latest_date is None or d > latest_date:
                latest_date = d

if not latest_date:
    latest_date = '2026-09-10'

latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
window_start = latest_dt - timedelta(days=120)  # ~4 months
window_start_str = window_start.strftime('%Y-%m-%d')
print(f"   Latest date: {latest_date}")
print(f"   4-month window: {window_start_str} → {latest_date}")

# ─── STEP 3: PROCESS CHECKINGS ───────────────────────────────────
print("\n[3/5] Processing check-ins...")

outlet_visits = defaultdict(list)   # dept_id -> list of (date_str, lat, lng, user_id)
user_visit_count = defaultdict(lambda: defaultdict(int))  # dept_id -> user_id -> count
outlet_latlng = {}   # dept_id -> (lat, lng)  (best lat/lng from checkings)

total_check = 0
in_window = 0
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        total_check += 1
        did = r.get('department_id') or ''
        ca = r.get('created_at') or ''
        date_str = ca[:10]
        if not did or not date_str or date_str < window_start_str:
            continue
        lat = r.get('lat') or ''
        lng = r.get('long') or ''
        uid = r.get('user_id') or ''
        outlet_visits[did].append(date_str)
        user_visit_count[did][uid] += 1
        if lat and lng and did not in outlet_latlng:
            try:
                flat, flng = float(lat), float(lng)
                if 20 < flat < 27 and 88 < flng < 93:
                    outlet_latlng[did] = (flat, flng)
            except:
                pass
        in_window += 1

print(f"   Total check-ins: {total_check:,}")
print(f"   In 4-month window: {in_window:,}")
print(f"   Unique outlets visited: {len(outlet_visits):,}")

# ─── STEP 4: PROCESS ORDERS ──────────────────────────────────────
print("\n[4/5] Processing orders (revenue)...")

outlet_revenue = defaultdict(float)   # buyer_dept_id -> 4M revenue
outlet_orders_count = defaultdict(int)
outlet_sr_from_orders = {}   # buyer_dept_id -> SR name (most common)
outlet_sr_votes = defaultdict(lambda: defaultdict(int))
outlet_territory_from_orders = {}  # buyer_dept_id -> territory string
outlet_monthly_rev = defaultdict(lambda: defaultdict(float))  # dept_id -> month -> rev

total_order_rows = 0
order_in_window = 0

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        total_order_rows += 1
        ca = r.get('created_at') or ''
        date_str = ca[:10]
        status = r.get('order_status') or ''
        if status == 'cancelled' or not date_str or date_str < window_start_str:
            continue
        bid = r.get('buyer_department_id') or ''
        if not bid:
            continue
        try:
            amt = float(r.get('amount') or 0)
        except:
            amt = 0.0
        sr = r.get('created_name') or ''
        territory = r.get('buyer_department_territory') or r.get('managed_territory') or ''
        month = date_str[:7]

        outlet_revenue[bid] += amt
        outlet_orders_count[bid] += 1
        if sr:
            outlet_sr_votes[bid][sr] += 1
        if territory and bid not in outlet_territory_from_orders:
            outlet_territory_from_orders[bid] = territory
        outlet_monthly_rev[bid][month] += amt
        order_in_window += 1

# Resolve SR names (most common per outlet)
for bid, votes in outlet_sr_votes.items():
    outlet_sr_from_orders[bid] = max(votes, key=votes.get)

print(f"   Total order rows: {total_order_rows:,}")
print(f"   In 4-month window: {order_in_window:,}")
print(f"   Revenue outlets: {len(outlet_revenue):,}")

# ─── STEP 5: COMPUTE HEALTH SCORES + BUILD OUTLET DATA ───────────
print("\n[5/5] Computing health scores and building outlet data...")

# Get all outlet IDs that have lat/lng (either from dept or checkings)
all_outlet_ids = set()
for did, d in dept_master.items():
    if d.get('lat') and d.get('lng') and d['dept_type'] not in ('1', '2', '3'):
        all_outlet_ids.add(did)
all_outlet_ids.update(outlet_latlng.keys())
all_outlet_ids.update(outlet_visits.keys())

print(f"   Total outlet candidates: {len(all_outlet_ids):,}")

# Compute percentile benchmarks for normalization
rev_vals = sorted(outlet_revenue.values())
vis_vals = sorted(len(v) for v in outlet_visits.values())

def percentile(lst, p):
    if not lst: return 1
    idx = int(len(lst) * p / 100)
    return max(1, lst[min(idx, len(lst)-1)])

p75_rev = percentile(rev_vals, 75)
p75_vis = percentile(vis_vals, 75)
print(f"   P75 Revenue: {p75_rev:,.0f}")
print(f"   P75 Visits: {p75_vis}")

latest_dt_ts = latest_dt

def compute_health_score(did, visits_list, revenue, last_visit_str, monthly_rev_dict):
    # 1. Revenue Performance (30%)
    rev_score = min(100, (revenue / p75_rev) * 100) if revenue > 0 else 0

    # 2. Visit Frequency (25%)
    n_visits = len(visits_list)
    vis_score = min(100, (n_visits / p75_vis) * 100) if n_visits > 0 else 0

    # 3. Recent Activity (20%) — days since last visit
    if last_visit_str:
        try:
            lv_dt = datetime.strptime(last_visit_str, '%Y-%m-%d')
            days_since = (latest_dt_ts - lv_dt).days
            if days_since <= 7: rec_score = 100
            elif days_since <= 14: rec_score = 85
            elif days_since <= 21: rec_score = 70
            elif days_since <= 30: rec_score = 55
            elif days_since <= 60: rec_score = 30
            else: rec_score = 10
        except:
            rec_score = 0
            days_since = 999
    else:
        rec_score = 0
        days_since = 999

    # 4. Productivity (15%) — rev per visit
    avg_rpv = revenue / n_visits if n_visits > 0 else 0
    p75_rpv = p75_rev / max(1, p75_vis)
    prod_score = min(100, (avg_rpv / p75_rpv) * 100) if avg_rpv > 0 else 0

    # 5. Recency Consistency (10%) — active months / 4
    active_months = len(monthly_rev_dict)
    consist_score = (active_months / 4) * 100

    score = (
        rev_score * 0.30 +
        vis_score * 0.25 +
        rec_score * 0.20 +
        prod_score * 0.15 +
        consist_score * 0.10
    )
    score = round(score)

    if score >= 70: status = 'G'   # Green / Strong
    elif score >= 40: status = 'Y'  # Yellow / Moderate
    else: status = 'R'              # Red / Weak

    return score, status, round(days_since), round(avg_rpv)

# Build outlet records
outlets_by_div = defaultdict(list)  # div_idx -> list of outlet arrays
div_stats = defaultdict(lambda: {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0,'visits':0,'districts':{}})
national_stats = {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0.0,'visits':0,'srs':set()}
district_stats = defaultdict(lambda: {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0,'visits':0,'div':'','div_idx':0})

skipped_no_latlon = 0
processed = 0

for did in all_outlet_ids:
    # Get lat/lng
    lat, lng = None, None
    if did in outlet_latlng:
        lat, lng = outlet_latlng[did]
    elif did in dept_master:
        dm = dept_master[did]
        try:
            flat, flng = float(dm.get('lat','') or 0), float(dm.get('lng','') or 0)
            if 20 < flat < 27 and 88 < flng < 93:
                lat, lng = flat, flng
        except:
            pass

    if lat is None or lng is None:
        skipped_no_latlon += 1
        continue

    # Get outlet info
    dm = dept_master.get(did, {})
    name = dm.get('name', f'Outlet {did}')
    if not name:
        name = f'Outlet {did}'
    code = dm.get('code', did)
    address = dm.get('address', '')

    # Get territory
    territory = outlet_territory_from_orders.get(did, '') or dm.get('territory_id', '')

    # Classify division + district
    div_name, div_idx = classify_division(territory, lat, lng)
    district = extract_district(territory) if territory and len(territory) > 5 else div_name

    # Visits + revenue
    visits_list = outlet_visits.get(did, [])
    revenue = outlet_revenue.get(did, 0.0)
    orders_cnt = outlet_orders_count.get(did, 0)
    monthly_rev = outlet_monthly_rev.get(did, {})
    last_visit = max(visits_list) if visits_list else ''

    # SR info
    sr_from_visits = ''
    if did in user_visit_count:
        # top user_id - we'll use order SR name as primary
        pass
    sr_name = outlet_sr_from_orders.get(did, '') or sr_from_visits or ''

    # SR top visitors
    sr_votes = outlet_sr_votes.get(did, {})
    top_srs = sorted(sr_votes.items(), key=lambda x: -x[1])[:3]

    # Skip if no activity at all (no visits AND no revenue in 4M window)
    if not visits_list and revenue == 0:
        # Still include if it's a registered outlet with valid coords
        if not dm.get('name'):
            continue

    # Health score
    score, status, days_since, avg_rpv = compute_health_score(
        did, visits_list, revenue, last_visit, monthly_rev
    )

    n_visits = len(visits_list)

    # Monthly revenue trend (last 4 months)
    # Get all months in window and fill 0 for missing
    months_in_window = []
    for i in range(3, -1, -1):
        m = (latest_dt - timedelta(days=30*i)).strftime('%Y-%m')
        months_in_window.append(m)
    trend = [round(monthly_rev.get(m, 0)) for m in months_in_window]

    # Compact array format:
    # [lat, lng, id, name(trunc), div_idx, district, score, status, rev4m, visits, lastVisit, daysSince, srName, orders, avgRPV, trend4]
    name_trunc = name[:40]
    sr_trunc = sr_name[:25] if sr_name else 'N/A'
    dist_trunc = district[:20]

    outlet_arr = [
        round(lat, 6), round(lng, 6),
        did,
        name_trunc,
        div_idx,
        dist_trunc,
        score,
        status,   # G/Y/R
        round(revenue),
        n_visits,
        last_visit or '',
        min(days_since, 999),
        sr_trunc,
        orders_cnt,
        round(avg_rpv),
        trend
    ]

    outlets_by_div[div_idx].append(outlet_arr)
    processed += 1

    # Stats
    national_stats['outlets'] += 1
    national_stats['visits'] += n_visits
    national_stats['revenue'] += revenue
    if sr_name: national_stats['srs'].add(sr_name)
    if status == 'G': national_stats['strong'] += 1
    elif status == 'Y': national_stats['moderate'] += 1
    else: national_stats['weak'] += 1

    ds = div_stats[div_name]
    ds['outlets'] += 1
    ds['revenue'] += revenue
    ds['visits'] += n_visits
    if status == 'G': ds['strong'] += 1
    elif status == 'Y': ds['moderate'] += 1
    else: ds['weak'] += 1

    # District stats
    dist_key = f"{div_name}::{district}"
    dd = district_stats[dist_key]
    dd['outlets'] += 1
    dd['revenue'] += revenue
    dd['visits'] += n_visits
    dd['div'] = div_name
    dd['div_idx'] = div_idx
    dd['district'] = district
    if status == 'G': dd['strong'] += 1
    elif status == 'Y': dd['moderate'] += 1
    else: dd['weak'] += 1

print(f"   Processed: {processed:,} outlets")
print(f"   Skipped (no lat/lng): {skipped_no_latlon:,}")
print(f"   National: {national_stats['outlets']:,} | Strong:{national_stats['strong']:,} | Moderate:{national_stats['moderate']:,} | Weak:{national_stats['weak']:,}")
print(f"   Total 4M Revenue: BDT {national_stats['revenue']/1e9:.2f}B")

# ─── OUTPUT: PER-DIVISION JS FILES ───────────────────────────────
print("\nWriting per-division outlet JS files...")
DIV_NAMES = ['Dhaka','Chattogram','Rajshahi','Khulna','Barishal','Sylhet','Rangpur','Mymensingh']
for div_idx in range(8):
    outlets = outlets_by_div[div_idx]
    filename = fr'e:\ITL FINAL ADV ANALYSIS\ceo_outlets_D{div_idx}.js'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'// {DIV_NAMES[div_idx]} Division Outlets\n')
        f.write(f'CEO_OUTLETS[{div_idx}]=')
        json.dump(outlets, f, ensure_ascii=False, separators=(',',':'))
        f.write(';')
    size_kb = os.path.getsize(filename) / 1024
    print(f"   D{div_idx} {DIV_NAMES[div_idx]}: {len(outlets):,} outlets | {size_kb:.0f}KB")

# ─── OUTPUT: NATIONAL DATA JS ─────────────────────────────────────
print("\nWriting national data JS...")

# Division summary
div_summary = []
for div_name, div_idx in [(n,i) for n,_,i in DIV_MAP]:
    ds = div_stats.get(div_name, {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0,'visits':0})
    n_out = len(outlets_by_div[div_idx])
    # Division center coords (approximate)
    div_centers = {
        'Dhaka': [23.81, 90.41],
        'Chattogram': [22.54, 91.81],
        'Rajshahi': [24.37, 88.60],
        'Khulna': [22.81, 89.55],
        'Barishal': [22.70, 90.36],
        'Sylhet': [24.89, 91.87],
        'Rangpur': [25.74, 89.25],
        'Mymensingh': [24.75, 90.41],
    }
    div_summary.append({
        'idx': div_idx,
        'name': div_name,
        'center': div_centers.get(div_name, [23.8, 90.4]),
        'outlets': n_out,
        'strong': ds['strong'],
        'moderate': ds['moderate'],
        'weak': ds['weak'],
        'revenue': round(ds['revenue']),
        'visits': ds['visits']
    })

# District summary
district_list = []
for key, dd in district_stats.items():
    if dd['outlets'] < 2: continue
    district_list.append({
        'district': dd['district'],
        'div': dd['div'],
        'div_idx': dd['div_idx'],
        'outlets': dd['outlets'],
        'strong': dd['strong'],
        'moderate': dd['moderate'],
        'weak': dd['weak'],
        'revenue': round(dd['revenue']),
        'visits': dd['visits']
    })
district_list.sort(key=lambda x: -x['outlets'])

# Executive insights
def top_div_by(key, div_summary):
    return max(div_summary, key=lambda d: d[key])['name'] if div_summary else 'N/A'

def top_dist_by(key, district_list):
    return max(district_list, key=lambda d: d[key])['district'] if district_list else 'N/A'

total_srs = len(national_stats['srs'])
insights = {
    'strongest_division': top_div_by('revenue', div_summary),
    'highest_density': top_div_by('outlets', div_summary),
    'most_weak': top_div_by('weak', div_summary),
    'attention_outlets': national_stats['weak'],
    'top_revenue_division': top_div_by('revenue', div_summary),
    'top_district_outlets': top_dist_by('outlets', district_list),
    'top_district_revenue': top_dist_by('revenue', district_list),
    'top_weak_districts': [d['district'] for d in sorted(district_list, key=lambda x:-x['weak'])[:5]],
    'window_start': window_start_str,
    'window_end': latest_date,
    'total_srs': total_srs
}

national_out = {
    'kpis': {
        'total_outlets': national_stats['outlets'],
        'strong': national_stats['strong'],
        'moderate': national_stats['moderate'],
        'weak': national_stats['weak'],
        'revenue_4m': round(national_stats['revenue']),
        'total_visits': national_stats['visits'],
        'active_srs': total_srs
    },
    'divisions': div_summary,
    'districts': district_list[:300],   # Top 300 districts
    'insights': insights,
    'window': {'start': window_start_str, 'end': latest_date}
}

with open(r'e:\ITL FINAL ADV ANALYSIS\ceo_national.js', 'w', encoding='utf-8') as f:
    f.write('CEO_OUTLETS=new Array(8);\n')
    f.write('const CEO_NATIONAL=')
    json.dump(national_out, f, ensure_ascii=False, separators=(',',':'))
    f.write(';')

size_kb = os.path.getsize(r'e:\ITL FINAL ADV ANALYSIS\ceo_national.js') / 1024
print(f"   ceo_national.js: {size_kb:.0f}KB")

print("\n" + "=" * 60)
print("DATA PIPELINE COMPLETE")
print(f"Total Outlets: {national_stats['outlets']:,}")
print(f"Strong: {national_stats['strong']:,} | Moderate: {national_stats['moderate']:,} | Weak: {national_stats['weak']:,}")
print(f"4M Revenue: BDT {national_stats['revenue']/1e9:.2f}B")
print(f"Total Visits: {national_stats['visits']:,}")
print(f"Active SRs: {total_srs:,}")
print(f"Analysis Window: {window_start_str} → {latest_date}")
print("=" * 60)
