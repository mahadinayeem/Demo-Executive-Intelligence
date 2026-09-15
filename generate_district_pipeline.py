import csv, json, sys, os, math
from collections import defaultdict
from datetime import datetime, timedelta
from shapely.geometry import shape, Point

csv.field_size_limit(min(2147483647, sys.maxsize))
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("ACCURATE CEO OUTLET DATA PIPELINE (64 DISTRICTS GEOMETRY)")
print("=" * 60)

# 1. Load GeoJSON for 64 districts
with open('e:/ITL FINAL ADV ANALYSIS/bd_districts_geo.js', 'r', encoding='utf-8') as f:
    raw = f.read().replace('const BD_DISTRICTS_GEO = ', '').rstrip(';').strip()
    geo = json.loads(raw)

for feat in geo['features']:
    p = feat['properties']
    if p['district'] == "Cox'SBazar" or p['district'] == "Cox's Bazar":
        p['district'] = 'Coxs Bazar'
        p['name'] = 'Coxs Bazar'
    if p['district'] == 'Brahamanbaria':
        p['district'] = 'Brahmanbaria'
        p['name'] = 'Brahmanbaria'
    if p['district'] == 'Maulvibazar':
        p['district'] = 'Moulvibazar'
        p['name'] = 'Moulvibazar'
    if p['district'] == 'Netrakona':
        p['district'] = 'Netrokona'
        p['name'] = 'Netrokona'

# Resave cleaned bd_districts_geo.js
with open('e:/ITL FINAL ADV ANALYSIS/bd_districts_geo.js', 'w', encoding='utf-8') as f:
    f.write('const BD_DISTRICTS_GEO = ' + json.dumps(geo) + ';')

# Prepare polygons with bounding box for spatial search
district_polys = []
for feat in geo['features']:
    p = feat['properties']
    geom = shape(feat['geometry'])
    district_polys.append({
        'div': p['division'],
        'dist': p['district'],
        'bbox': geom.bounds, # minlng, minlat, maxlng, maxlat
        'geom': geom
    })

print(f"Loaded {len(district_polys)} district polygons.")

DIV_NAMES = ['Dhaka','Chattogram','Rajshahi','Khulna','Barishal','Sylhet','Rangpur','Mymensingh']
DIV_TO_IDX = {name: i for i, name in enumerate(DIV_NAMES)}

def find_div_district_by_coords(lat, lng):
    # Check bbox and containment
    pt = Point(lng, lat)
    for dp in district_polys:
        minlng, minlat, maxlng, maxlat = dp['bbox']
        if minlat <= lat <= maxlat and minlng <= lng <= maxlng:
            if dp['geom'].contains(pt):
                return dp['div'], dp['dist']
    # Fallback to nearest district polygon
    best_dist = 999.0
    best_div, best_dist_name = 'Dhaka', 'Dhaka'
    for dp in district_polys:
        d = dp['geom'].distance(pt)
        if d < best_dist:
            best_dist = d
            best_div = dp['div']
            best_dist_name = dp['dist']
    return best_div, best_dist_name

# Load dept master
print("\n[1/5] Loading dept master...")
dept_master = {}
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_dept.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        did = r.get('id', '')
        if not did: continue
        dept_master[did] = {
            'name': r.get('name', ''),
            'code': r.get('code', ''),
            'lat': r.get('lat', ''),
            'lng': r.get('long', ''),
            'territory_id': r.get('territory_id', ''),
            'address': r.get('address', '') or r.get('check_in_address', ''),
            'dept_type': r.get('department_type_id', ''),
            'status': r.get('status', 'active')
        }
print(f"   Loaded {len(dept_master):,} departments")

# Date window
print("\n[2/5] Determining 4-month window...")
latest_date = None
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        ca = r.get('created_at') or ''
        d = ca[:10]
        if d and d > '2020-01-01':
            if latest_date is None or d > latest_date:
                latest_date = d
if not latest_date: latest_date = '2026-09-10'
latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
window_start = latest_dt - timedelta(days=120)
window_start_str = window_start.strftime('%Y-%m-%d')
print(f"   Window: {window_start_str} -> {latest_date}")

# Checkings
print("\n[3/5] Processing check-ins...")
outlet_visits = defaultdict(list)
user_visit_count = defaultdict(lambda: defaultdict(int))
outlet_latlng = {}

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
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

print(f"   Unique visited outlets: {len(outlet_visits):,}")

# Orders
print("\n[4/5] Processing orders...")
outlet_revenue = defaultdict(float)
outlet_orders_count = defaultdict(int)
outlet_sr_votes = defaultdict(lambda: defaultdict(int))
outlet_sr_from_orders = {}
outlet_monthly_rev = defaultdict(lambda: defaultdict(float))

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        ca = r.get('created_at') or ''
        date_str = ca[:10]
        status = r.get('order_status') or ''
        if status == 'cancelled' or not date_str or date_str < window_start_str:
            continue
        bid = r.get('buyer_department_id') or ''
        if not bid: continue
        try:
            amt = float(r.get('amount') or 0)
        except:
            amt = 0.0
        sr = r.get('created_name') or ''
        month = date_str[:7]
        outlet_revenue[bid] += amt
        outlet_orders_count[bid] += 1
        if sr: outlet_sr_votes[bid][sr] += 1
        outlet_monthly_rev[bid][month] += amt

for bid, votes in outlet_sr_votes.items():
    outlet_sr_from_orders[bid] = max(votes, key=votes.get)

# Percentiles
rev_vals = sorted(outlet_revenue.values())
vis_vals = sorted(len(v) for v in outlet_visits.values())
def percentile(lst, p):
    if not lst: return 1
    idx = int(len(lst) * p / 100)
    return max(1, lst[min(idx, len(lst)-1)])

p75_rev = percentile(rev_vals, 75)
p75_vis = percentile(vis_vals, 75)

def compute_health_score(did, visits_list, revenue, last_visit_str, monthly_rev_dict):
    rev_score = min(100, (revenue / p75_rev) * 100) if revenue > 0 else 0
    n_visits = len(visits_list)
    vis_score = min(100, (n_visits / p75_vis) * 100) if n_visits > 0 else 0
    if last_visit_str:
        try:
            lv_dt = datetime.strptime(last_visit_str, '%Y-%m-%d')
            days_since = (latest_dt - lv_dt).days
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

    avg_rpv = revenue / n_visits if n_visits > 0 else 0
    p75_rpv = p75_rev / max(1, p75_vis)
    prod_score = min(100, (avg_rpv / p75_rpv) * 100) if avg_rpv > 0 else 0
    active_months = len(monthly_rev_dict)
    consist_score = (active_months / 4) * 100

    score = round(rev_score * 0.30 + vis_score * 0.25 + rec_score * 0.20 + prod_score * 0.15 + consist_score * 0.10)
    if score >= 70: status = 'G'
    elif score >= 40: status = 'Y'
    else: status = 'R'
    return score, status, round(days_since), round(avg_rpv)

# Process all outlets
print("\n[5/5] Spatial assignment of outlets to EXACT division & district...")
all_outlet_ids = set()
for did, d in dept_master.items():
    if d.get('lat') and d.get('lng') and d['dept_type'] not in ('1', '2', '3'):
        all_outlet_ids.add(did)
all_outlet_ids.update(outlet_latlng.keys())
all_outlet_ids.update(outlet_visits.keys())

outlets_by_div = defaultdict(list)
div_stats = defaultdict(lambda: {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0,'visits':0})
national_stats = {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0.0,'visits':0,'srs':set()}
district_stats = defaultdict(lambda: {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0,'visits':0,'div':'','div_idx':0})

months_in_window = []
for i in range(3, -1, -1):
    months_in_window.append((latest_dt - timedelta(days=30*i)).strftime('%Y-%m'))

processed = 0
for did in all_outlet_ids:
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
        continue

    dm = dept_master.get(did, {})
    name = dm.get('name') or f'Outlet {did}'
    
    # Exact spatial lookup
    div_name, district = find_div_district_by_coords(lat, lng)
    div_idx = DIV_TO_IDX.get(div_name, 0)

    visits_list = outlet_visits.get(did, [])
    revenue = outlet_revenue.get(did, 0.0)
    orders_cnt = outlet_orders_count.get(did, 0)
    monthly_rev = outlet_monthly_rev.get(did, {})
    last_visit = max(visits_list) if visits_list else ''
    sr_name = outlet_sr_from_orders.get(did, '')

    if not visits_list and revenue == 0 and not dm.get('name'):
        continue

    score, status, days_since, avg_rpv = compute_health_score(
        did, visits_list, revenue, last_visit, monthly_rev
    )
    n_visits = len(visits_list)
    trend = [round(monthly_rev.get(m, 0)) for m in months_in_window]

    outlet_arr = [
        round(lat, 6), round(lng, 6),
        did,
        name[:40],
        div_idx,
        district[:20],
        score,
        status,
        round(revenue),
        n_visits,
        last_visit or '',
        min(days_since, 999),
        sr_name[:25] if sr_name else 'N/A',
        orders_cnt,
        round(avg_rpv),
        trend
    ]

    outlets_by_div[div_idx].append(outlet_arr)
    processed += 1

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

print(f"Processed: {processed:,} outlets.")

# Write per-division JS
for div_idx in range(8):
    outlets = outlets_by_div[div_idx]
    filename = fr'e:\ITL FINAL ADV ANALYSIS\ceo_outlets_D{div_idx}.js'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'// {DIV_NAMES[div_idx]} Division Outlets\n')
        f.write(f'CEO_OUTLETS[{div_idx}]=')
        json.dump(outlets, f, ensure_ascii=False, separators=(',',':'))
        f.write(';')
    print(f"   D{div_idx} {DIV_NAMES[div_idx]}: {len(outlets):,} outlets")

# Build division summary
div_summary = []
for div_idx, div_name in enumerate(DIV_NAMES):
    ds = div_stats.get(div_name, {'outlets':0,'strong':0,'moderate':0,'weak':0,'revenue':0,'visits':0})
    div_summary.append({
        'idx': div_idx,
        'name': div_name,
        'outlets': ds['outlets'],
        'strong': ds['strong'],
        'moderate': ds['moderate'],
        'weak': ds['weak'],
        'revenue': round(ds['revenue']),
        'visits': ds['visits']
    })

# Build district summary
district_list = []
for key, dd in district_stats.items():
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

national_out = {
    'kpis': {
        'total_outlets': national_stats['outlets'],
        'strong': national_stats['strong'],
        'moderate': national_stats['moderate'],
        'weak': national_stats['weak'],
        'revenue_4m': round(national_stats['revenue']),
        'total_visits': national_stats['visits'],
        'active_srs': len(national_stats['srs'])
    },
    'divisions': div_summary,
    'districts': district_list,
    'window': {'start': window_start_str, 'end': latest_date}
}

with open(r'e:\ITL FINAL ADV ANALYSIS\ceo_national.js', 'w', encoding='utf-8') as f:
    f.write('CEO_OUTLETS=new Array(8);\n')
    f.write('const CEO_NATIONAL=')
    json.dump(national_out, f, ensure_ascii=False, separators=(',',':'))
    f.write(';')

print("Successfully regenerated ceo_national.js and all division outlet files!")
