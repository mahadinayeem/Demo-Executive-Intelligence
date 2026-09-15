"""
MODULE 4 — FIELD SALES PRODUCTIVITY & EMPLOYEE DIAGNOSTICS
PerformancePulse Analyzer™
Single pass over itl_orders.csv + single pass over itl_checkings.csv
Outputs module4_data.json + module4_data.js
"""
import csv, json, sys, math
from datetime import datetime, timedelta
from collections import defaultdict

csv.field_size_limit(2147483647)

sys.stdout.reconfigure(encoding='utf-8')
print("=" * 60)
print("=== MODULE 4 — PERFORMANCEPULSE ANALYZER ===")
print("=" * 60)

def parse_dt(s):
    if not s: return None
    try: return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    except: pass
    try: return datetime.strptime(s[:10], "%Y-%m-%d")
    except: return None

def parse_date(s):
    if not s: return None
    try: return datetime.strptime(s[:10], "%Y-%m-%d")
    except: return None

def safe_float(v, default=0.0):
    try: return float(v) if v else default
    except: return default

def median(lst):
    if not lst: return 0
    s = sorted(lst); mid = len(s)//2
    return s[mid] if len(s)%2 else (s[mid-1]+s[mid])/2

def is_valid_month(date_str):
    d = parse_date(date_str)
    if not d: return False
    if d.year == 2026 and d.month == 9: return False
    return True

# ── 1. SINGLE PASS OVER ORDERS ───────────────────────────────────────────────
print("\n[1/4] Processing itl_orders.csv in a single pass...")
cancelled = {'Cancelled', 'cancelled', 'cancel', 'Cancel'}
terr_name_map = {}
outlet_date_orders = defaultdict(list)
sr_orders = defaultdict(list)
sr_info = {}
n_orders = 0

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    for row in csv.DictReader(f):
        tid = (row.get('seller_department_territory') or '').strip()
        tn  = (row.get('seller_department_name') or '').strip()
        if tid and tn and tid not in terr_name_map:
            terr_name_map[tid] = tn

        status = row.get('latest_status','') or row.get('order_status','')
        if status in cancelled: continue
        amt = safe_float(row.get('amount', 0))
        if amt <= 0 or amt > 500000: continue
        
        sr_id   = (row.get('created_id') or '').strip()
        sr_name = (row.get('created_name') or '').strip()
        sr_code = (row.get('created_code') or '').strip()
        odate   = (row.get('order_date') or '')[:10]
        buyer   = (row.get('buyer_department_id') or '').strip()
        order_id= (row.get('order_id') or row.get('id') or '').strip()
        sku     = (row.get('product_sku') or '').strip()
        
        if not is_valid_month(odate): continue
        
        if buyer and odate:
            outlet_date_orders[(buyer, odate)].append(amt)
            
        if sr_id and sr_name:
            if sr_id not in sr_info:
                sr_info[sr_id] = {'name': sr_name, 'code': sr_code,
                                   'territory': terr_name_map.get(tid, tid)}
            elif not sr_info[sr_id].get('territory') and tid:
                sr_info[sr_id]['territory'] = terr_name_map.get(tid, tid)
                
            sr_orders[sr_id].append({'order_id':order_id,'date':odate,'amount':amt,'buyer':buyer,'sku':sku})
            n_orders += 1

print(f"    Valid orders: {n_orders:,} | SRs with orders: {len(sr_orders):,} | Territories: {len(terr_name_map):,}")

# ── 2. SINGLE PASS OVER CHECKINGS ─────────────────────────────────────────────
print("\n[2/4] Processing itl_checkings.csv in a single pass...")
sr_visits = defaultdict(list)
all_visits_flat = []
n_visits = 0

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    for row in csv.DictReader(f):
        uid   = (row.get('user_id') or '').strip()
        dept  = (row.get('department_id') or '').strip()
        cin   = row.get('created_at','') or ''
        cout  = row.get('checked_out_at','') or ''
        vdate = cin[:10]
        if not uid or not vdate: continue
        if not is_valid_month(vdate): continue
        dt_in  = parse_dt(cin)
        dt_out = parse_dt(cout)
        duration = None
        if dt_in and dt_out and dt_out > dt_in:
            dur_mins = (dt_out - dt_in).total_seconds() / 60.0
            if 0 < dur_mins < 480:
                duration = round(dur_mins, 1)
        visit = {'date': vdate, 'dept': dept, 'duration': duration}
        sr_visits[uid].append(visit)
        all_visits_flat.append((uid, dept, vdate, duration))
        n_visits += 1

print(f"    Valid visits: {n_visits:,} | SRs with visits: {len(sr_visits):,}")

# ── 3. COMPUTE SR PROFILES & CLUSTERING ───────────────────────────────────────
print("\n[3/4] Computing SR metrics & personas...")
all_sr_ids = set(sr_orders.keys()) | set(sr_visits.keys())
sr_profiles = []

for sr_id in all_sr_ids:
    info   = sr_info.get(sr_id, {})
    orders = sr_orders.get(sr_id, [])
    visits = sr_visits.get(sr_id, [])
    if not info and not orders and len(visits) < 5: continue

    sr_name = info.get('name', f"SR #{sr_id}")
    sr_code = info.get('code', '')
    sr_terr = info.get('territory', 'Unknown Territory')

    total_revenue = sum(o['amount'] for o in orders)
    unique_orders = len(set(o['order_id'] for o in orders))
    outlet_ordered = set(o['buyer'] for o in orders if o['buyer'])
    aov = total_revenue / unique_orders if unique_orders > 0 else 0

    all_dates = sorted(set(o['date'] for o in orders) | set(v['date'] for v in visits))
    working_days = max(1, len(set(all_dates)))

    total_visits = len(visits)
    unique_outlets_visited = len(set(v['dept'] for v in visits if v['dept']))
    unique_visit_days = len(set(v['date'] for v in visits))

    durations = [v['duration'] for v in visits if v['duration'] is not None]
    avg_duration = round(sum(durations)/len(durations), 1) if durations else 0.0

    visits_per_day = round(total_visits / working_days, 1) if working_days else 0.0
    daily_revenue  = round(total_revenue / working_days, 0) if working_days else 0.0

    # Conversion rate
    conversion_rate = round(unique_orders / total_visits * 100, 1) if total_visits > 0 else (100.0 if unique_orders > 0 else 0.0)
    conversion_rate = min(100.0, conversion_rate)

    strike_rate = round(len(outlet_ordered) / unique_outlets_visited * 100, 1) if unique_outlets_visited > 0 else 0.0
    strike_rate = min(100.0, strike_rate)

    sr_profiles.append({
        'id': sr_id,
        'name': sr_name,
        'code': sr_code,
        'territory': sr_terr,
        'revenue': round(total_revenue, 2),
        'orders': unique_orders,
        'aov': round(aov, 0),
        'visits': total_visits,
        'outlets_visited': unique_outlets_visited,
        'outlets_ordered': len(outlet_ordered),
        'working_days': working_days,
        'visits_per_day': visits_per_day,
        'daily_revenue': daily_revenue,
        'avg_duration_mins': avg_duration,
        'conversion_rate': conversion_rate,
        'strike_rate': strike_rate,
    })

sr_profiles.sort(key=lambda x: x['revenue'], reverse=True)
for i, p in enumerate(sr_profiles):
    p['rank'] = i + 1

total_company_rev = sum(p['revenue'] for p in sr_profiles)
running_rev = 0
for p in sr_profiles:
    running_rev += p['revenue']
    p['rev_share_pct'] = round(p['revenue'] / total_company_rev * 100, 2) if total_company_rev else 0
    p['cumul_pct']     = round(running_rev / total_company_rev * 100, 2) if total_company_rev else 0

# Benchmark medians for active SRs
active_srs = [p for p in sr_profiles if p['revenue'] > 0 or p['visits'] >= 10]
med_rev    = median([p['revenue'] for p in active_srs]) if active_srs else 1
med_conv   = median([p['conversion_rate'] for p in active_srs]) if active_srs else 1
med_vpd    = median([p['visits_per_day'] for p in active_srs]) if active_srs else 1
med_strike = median([p['strike_rate'] for p in active_srs if p['strike_rate'] > 0]) if active_srs else 50
med_aov    = median([p['aov'] for p in active_srs if p['aov'] > 0]) if active_srs else 1000

for p in sr_profiles:
    rev    = p['revenue']
    conv   = p['conversion_rate']
    vpd    = p['visits_per_day']
    vis    = p['visits']
    strike = p['strike_rate']
    aov    = p['aov']

    # Personas & Quadrants
    if rev >= med_rev and conv >= med_conv:
        persona = 'High-Efficiency Closer'
        quadrant = 'Star Performers'
        color = '#10b981'
    elif rev >= med_rev and conv < med_conv:
        persona = 'High-Volume Runner'
        quadrant = 'Volume Drivers'
        color = '#3b82f6'
    elif rev < med_rev and conv >= med_conv:
        persona = 'Targeted Specialist'
        quadrant = 'High Potential'
        color = '#f59e0b'
    elif rev < med_rev and conv < med_conv:
        if vis < 20 and rev == 0:
            persona = 'Inactive / Dormant'
            quadrant = 'Dormant'
            color = '#64748b'
        else:
            persona = 'Low-Productivity Laggard'
            quadrant = 'Needs Intervention'
            color = '#ef4444'
    else:
        persona = 'Standard Performer'
        quadrant = 'Core Base'
        color = '#8b5cf6'

    # Training Intervention Diagnosis (Item 6 & 7)
    if vis == 0 and rev == 0:
        diagnosis = "Inactive Employee"
        intervention = "HR Status Verification & Account Audit"
        gap_type = "Dormant"
    elif vpd >= med_vpd and strike < med_strike:
        diagnosis = "Pitching & Closing Skill Gap"
        intervention = "Closing & Objection Handling Training (SR reaches outlets but fails to close orders)"
        gap_type = "Closing Gap"
    elif vpd < med_vpd and strike >= med_strike:
        diagnosis = "Route Discipline & Work Rate Deficit"
        intervention = "PJP Route Optimization & Daily Call Discipline (SR closes well but visits too few outlets)"
        gap_type = "Route Gap"
    elif strike >= med_strike and aov < med_aov:
        diagnosis = "Basket Size & Upselling Underperformance"
        intervention = "Trade Scheme Pitching & Multi-SKU Basket Building Coaching"
        gap_type = "Drop Size Gap"
    elif vpd >= 35 and conv < 10.0:
        diagnosis = "Superficial Check-in Signature"
        intervention = "Supervisor Joint-Visit Audit & Outlet Verification"
        gap_type = "Activity Audit"
    elif vpd < med_vpd and strike < med_strike:
        diagnosis = "Comprehensive Skill & Motivation Gap"
        intervention = "14-Day Supervised Field Shadowing with Top SR Mentor"
        gap_type = "Full Pipeline Gap"
    else:
        diagnosis = "Balanced Core Performer"
        intervention = "Target Expansion & Key Account Leadership Track"
        gap_type = "Growth Track"

    # Red Flag
    red_flag = False
    red_flag_reason = []
    if vis >= 50 and rev == 0:
        red_flag = True
        red_flag_reason.append(f"High visits ({vis}) with ZERO revenue")
    elif vis >= 100 and conv < 2.0:
        red_flag = True
        red_flag_reason.append(f"Excessive visits ({vis}) with near-zero conversion ({conv}%)")
    elif vpd > 40 and conv < 5.0:
        red_flag = True
        red_flag_reason.append(f"Unrealistic visit pace ({vpd} visits/day) with poor conversion ({conv}%)")
    elif rev > 500000 and vis < 5:
        red_flag = True
        red_flag_reason.append("Ghost Orders (High revenue with no recorded visit audit trail)")

    p['persona'] = persona
    p['quadrant'] = quadrant
    p['persona_color'] = color
    p['diagnosis'] = diagnosis
    p['intervention'] = intervention
    p['gap_type'] = gap_type
    p['is_red_flag'] = red_flag
    p['red_flag_reason'] = " | ".join(red_flag_reason) if red_flag else "Normal"

print(f"    Total SR Profiles: {len(sr_profiles):,}")

# ── 4. ANALYTICS & AGGREGATIONS ───────────────────────────────────────────────
print("\n[4/4] Computing latency, visit buckets & Pareto summaries...")

# Visit Quality Buckets
buckets = {
    'Superficial (<3 mins)': {'min': 0, 'max': 3, 'visits': 0, 'conv_orders': 0, 'rev': 0.0},
    'Brief (3–7 mins)':       {'min': 3, 'max': 7, 'visits': 0, 'conv_orders': 0, 'rev': 0.0},
    'Standard (7–15 mins)':   {'min': 7, 'max': 15, 'visits': 0, 'conv_orders': 0, 'rev': 0.0},
    'Quality Deep (15+ mins)':{'min': 15, 'max': 9999, 'visits': 0, 'conv_orders': 0, 'rev': 0.0},
}
unknown_bucket = {'visits': 0, 'conv_orders': 0, 'rev': 0.0}

for uid, dept, vdate, dur in all_visits_flat:
    b_found = None
    if dur is not None:
        for b_name, b_data in buckets.items():
            if b_data['min'] <= dur < b_data['max']:
                b_found = b_data
                break
    if not b_found:
        b_found = unknown_bucket
    b_found['visits'] += 1
    
    # Check same-day conversion
    same_day_ords = outlet_date_orders.get((dept, vdate), [])
    if same_day_ords:
        b_found['conv_orders'] += len(same_day_ords)
        b_found['rev'] += sum(same_day_ords)

visit_quality_summary = []
for b_name, b_data in buckets.items():
    v = b_data['visits']
    co = b_data['conv_orders']
    cr = round(co / v * 100, 2) if v > 0 else 0.0
    aov = round(b_data['rev'] / co, 0) if co > 0 else 0.0
    visit_quality_summary.append({
        'bucket': b_name,
        'visits': v,
        'converted_orders': co,
        'conversion_rate_pct': cr,
        'revenue_bdt': round(b_data['rev'], 2),
        'aov_bdt': aov
    })

# Visit-to-Conversion Latency
latency_counts = defaultdict(int)
sample_visits = all_visits_flat[:100000] if len(all_visits_flat) > 100000 else all_visits_flat
for uid, dept, vdate, dur in sample_visits:
    if not dept: continue
    v_dt = parse_date(vdate)
    if not v_dt: continue
    for day_lag in range(15):
        chk_dt = v_dt + timedelta(days=day_lag)
        chk_str = chk_dt.strftime('%Y-%m-%d')
        ords = outlet_date_orders.get((dept, chk_str), [])
        if ords:
            latency_counts[day_lag] += len(ords)
            break

latency_summary = []
total_sample_conversions = sum(latency_counts.values()) or 1
cumul_conv = 0
for day in range(15):
    cnt = latency_counts.get(day, 0)
    cumul_conv += cnt
    latency_summary.append({
        'day_lag': day,
        'day_label': 'Same Day' if day == 0 else f"+{day} Days",
        'order_count': cnt,
        'pct_of_conversions': round(cnt / total_sample_conversions * 100, 1),
        'cumul_pct': round(cumul_conv / total_sample_conversions * 100, 1)
    })

# Revenue Concentration (Pareto)
n_active_srs = len([p for p in sr_profiles if p['revenue'] > 0])
top10_count = max(1, math.ceil(n_active_srs * 0.10))
top20_count = max(1, math.ceil(n_active_srs * 0.20))
top30_count = max(1, math.ceil(n_active_srs * 0.30))

rev_top10 = sum(p['revenue'] for p in sr_profiles[:top10_count])
rev_top20 = sum(p['revenue'] for p in sr_profiles[:top20_count])
rev_top30 = sum(p['revenue'] for p in sr_profiles[:top30_count])

pareto_concentration = {
    'total_active_srs': n_active_srs,
    'total_revenue': round(total_company_rev, 2),
    'top_10pct_srs': {'count': top10_count, 'revenue': round(rev_top10, 2), 'share_pct': round(rev_top10/total_company_rev*100, 1) if total_company_rev else 0},
    'top_20pct_srs': {'count': top20_count, 'revenue': round(rev_top20, 2), 'share_pct': round(rev_top20/total_company_rev*100, 1) if total_company_rev else 0},
    'top_30pct_srs': {'count': top30_count, 'revenue': round(rev_top30, 2), 'share_pct': round(rev_top30/total_company_rev*100, 1) if total_company_rev else 0},
}

# Persona breakdown
persona_counts = defaultdict(lambda: {'count': 0, 'revenue': 0.0, 'visits': 0, 'orders': 0})
for p in sr_profiles:
    prs = p['persona']
    persona_counts[prs]['count'] += 1
    persona_counts[prs]['revenue'] += p['revenue']
    persona_counts[prs]['visits'] += p['visits']
    persona_counts[prs]['orders'] += p['orders']

persona_summary = []
for prs, pdata in persona_counts.items():
    persona_summary.append({
        'persona': prs,
        'sr_count': pdata['count'],
        'revenue_bdt': round(pdata['revenue'], 2),
        'rev_share_pct': round(pdata['revenue'] / total_company_rev * 100, 1) if total_company_rev else 0,
        'total_visits': pdata['visits'],
        'total_orders': pdata['orders'],
        'avg_aov': round(pdata['revenue'] / pdata['orders'], 0) if pdata['orders'] > 0 else 0
    })

# Red Flag Employees List
red_flag_list = [p for p in sr_profiles if p['is_red_flag']]

# Territory Performance Rollup
terr_rollup = defaultdict(lambda: {'srs': 0, 'revenue': 0.0, 'visits': 0, 'orders': 0, 'red_flags': 0})
for p in sr_profiles:
    t = p['territory']
    terr_rollup[t]['srs'] += 1
    terr_rollup[t]['revenue'] += p['revenue']
    terr_rollup[t]['visits'] += p['visits']
    terr_rollup[t]['orders'] += p['orders']
    if p['is_red_flag']: terr_rollup[t]['red_flags'] += 1

territory_summary = []
for tname, tdata in terr_rollup.items():
    if not tname or tname == 'Unknown Territory': continue
    cr = round(tdata['orders'] / tdata['visits'] * 100, 1) if tdata['visits'] > 0 else 0.0
    territory_summary.append({
        'territory': tname,
        'sr_count': tdata['srs'],
        'revenue_bdt': round(tdata['revenue'], 2),
        'total_visits': tdata['visits'],
        'total_orders': tdata['orders'],
        'conversion_rate_pct': min(100.0, cr),
        'red_flag_srs': tdata['red_flags']
    })
territory_summary.sort(key=lambda x: x['revenue_bdt'], reverse=True)

# Export CSVs for users
print("\n[Exporting detailed CSVs]...")
with open(r'e:\ITL FINAL ADV ANALYSIS\module4_sr_performance_ranking.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Rank','SR_ID','SR_Name','SR_Code','Territory','Persona','Quadrant','Revenue_BDT','Revenue_Share_Pct','Orders','AOV_BDT','Total_Visits','Visits_Per_Day','Conversion_Rate_Pct','Strike_Rate_Pct','Working_Days','Avg_Visit_Duration_Mins','Is_Red_Flag','Red_Flag_Reason'])
    for p in sr_profiles:
        w.writerow([p['rank'], p['id'], p['name'], p['code'], p['territory'], p['persona'], p['quadrant'], p['revenue'], p['rev_share_pct'], p['orders'], p['aov'], p['visits'], p['visits_per_day'], p['conversion_rate'], p['strike_rate'], p['working_days'], p['avg_duration_mins'], 'YES' if p['is_red_flag'] else 'NO', p['red_flag_reason']])

with open(r'e:\ITL FINAL ADV ANALYSIS\module4_red_flag_employees.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Rank','SR_ID','SR_Name','SR_Code','Territory','Total_Visits','Total_Orders','Revenue_BDT','Visits_Per_Day','Conversion_Rate_Pct','Red_Flag_Reason'])
    for p in red_flag_list:
        w.writerow([p['rank'], p['id'], p['name'], p['code'], p['territory'], p['visits'], p['orders'], p['revenue'], p['visits_per_day'], p['conversion_rate'], p['red_flag_reason']])

# Assemble JSON
final_data = {
    'summary': {
        'total_srs': len(sr_profiles),
        'active_srs': n_active_srs,
        'total_revenue': round(total_company_rev, 2),
        'total_orders': sum(p['orders'] for p in sr_profiles),
        'total_visits': sum(p['visits'] for p in sr_profiles),
        'avg_conversion_rate': round(sum(p['orders'] for p in sr_profiles) / sum(p['visits'] for p in sr_profiles) * 100, 1) if sum(p['visits'] for p in sr_profiles) > 0 else 0,
        'red_flags_count': len(red_flag_list)
    },
    'visit_quality': visit_quality_summary,
    'latency': latency_summary,
    'pareto_concentration': pareto_concentration,
    'personas': persona_summary,
    'territories': territory_summary,
    'red_flags': red_flag_list[:100], # Top 100 for fast UI display
    'sr_rankings': sr_profiles[:250], # Top 250 for fast UI display
}

with open(r'e:\ITL FINAL ADV ANALYSIS\module4_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

with open(r'e:\ITL FINAL ADV ANALYSIS\module4_data.js', 'w', encoding='utf-8') as f:
    f.write("window.MODULE4_DATA = " + json.dumps(final_data, ensure_ascii=False) + ";")

print("\n✓ SUCCESS: Module 4 data pipeline generated successfully!")
print(f"  → JSON: module4_data.json ({len(json.dumps(final_data)):,} bytes)")
print(f"  → JS:   module4_data.js")
print(f"  → CSVs: module4_sr_performance_ranking.csv, module4_red_flag_employees.csv")
