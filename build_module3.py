import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta

csv.field_size_limit(2147483647)
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("=== MODULE 3 DATA BUILDER (RETAIL SPOTLIGHT™) ===")
print("=" * 60)

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
ACTIVE_DAYS         = 30     # Last 30 days = Active
AT_RISK_DAYS        = 60     # 31-60 days = At-Risk (Silent for 1 month)
OUTLIER_THRESHOLD   = 500000 # Max single order line amount (filters >5 Lakh outliers)
SILENT_BLEED_THRESHOLD = 0.50  # >50% AOV drop
RED_FLAG_VISIT_COUNT   = 5     # >5 visits with 0 orders
CHURN_RISK_MULTIPLIER  = 2.0   # 2.0x avg gap = at risk
CHURN_HIGH_MULTIPLIER  = 2.5   # 2.5x avg gap = high risk

# Baseline date: 2026-08-31 (excluding incomplete September 2026 as per standard)
MAX_DATE = datetime(2026, 8, 31)
print(f"Analysis Baseline Date: {MAX_DATE.date()}")

def days_ago(date_str):
    if not date_str:
        return 9999
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return (MAX_DATE - dt).days
    except:
        return 9999

def is_valid_month(date_str):
    if not date_str: return False
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        if d.year == 2026 and d.month == 9: return False
        if d > MAX_DATE: return False
        return True
    except:
        return False

# ─── 1. BUILD TERRITORY & OUTLET MASTER MAP ─────────────────────────────────
print("\n[1/4] Building territory & outlet master lookup maps...")
dept_map = {}
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_dept.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        c = (r.get('code') or '').strip()
        i = (r.get('id') or '').strip()
        name = (r.get('name') or '').strip()
        owner = (r.get('owner_name') or '').strip()
        phone = (r.get('phone_no') or '').strip()
        addr = (r.get('address') or '').strip()
        record = {'name': name, 'owner': owner, 'phone': phone, 'address': addr}
        if c: dept_map[c] = record
        if i and i not in dept_map: dept_map[i] = record
print(f"  Outlets mapped from dept master: {len(dept_map):,}")

territory_name_map = {}
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sdt = (r.get('seller_department_territory') or '').strip()
        sdn = (r.get('seller_department_name') or '').strip()
        if sdt and sdn and sdt not in territory_name_map:
            territory_name_map[sdt] = sdn
print(f"  Territories resolved: {len(territory_name_map):,}")

# ─── 2. PROCESS ALL ORDER LINES ──────────────────────────────────────────────
print("\n[2/4] Processing orders (aggregated by unique order_id and buyer)...")

# Data structure per outlet
outlets = defaultdict(lambda: {
    'orders': 0,
    'revenue': 0.0,
    'first_order_date': None,
    'last_order_date': None,
    'recent_revenue':  0.0,
    'recent_orders':   0,
    'historical_revenue': 0.0,
    'historical_orders':  0,
    'skus_set': set(),
    'order_dates_set': set(),
    'territory': '',
    'last_visit_date': None,
    'total_visits': 0,
    'recent_visits': 0,
    'churn_period_visits': 0,
})

order_summary = defaultdict(lambda: {'buyer': '', 'date': '', 'amount': 0.0, 'territory': '', 'skus': set()})

total_revenue = 0.0
n_order_lines = 0

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        status = r.get('latest_status','') or r.get('order_status','')
        if status in {'cancelled', 'Cancelled', 'cancel', 'Cancel'}:
            continue
        try:
            amt = float(r.get('amount', 0) or 0)
        except:
            amt = 0.0
            
        if amt <= 0 or amt > OUTLIER_THRESHOLD:
            continue
            
        buyer = (r.get('buyer_department_id') or r.get('buyer_department_code') or '').strip()
        if not buyer:
            continue

        created_at = (r.get('order_date') or r.get('created_at') or '')[:10]
        if not is_valid_month(created_at):
            continue

        oid = (r.get('order_id') or r.get('id') or '').strip()
        territory_raw = (r.get('seller_department_territory') or '').strip()
        territory = territory_name_map.get(territory_raw, territory_raw) or 'National Retail'
        sku = (r.get('product_sku') or '').strip()

        # Aggregate line item into order
        ord_key = (oid, buyer) if oid else (f"no_id_{n_order_lines}", buyer)
        order_summary[ord_key]['buyer'] = buyer
        order_summary[ord_key]['date'] = created_at
        order_summary[ord_key]['amount'] += amt
        order_summary[ord_key]['territory'] = territory
        if sku:
            order_summary[ord_key]['skus'].add(sku)
            
        n_order_lines += 1

print(f"  Valid order lines: {n_order_lines:,} | Unique orders assembled: {len(order_summary):,}")

# Populate outlets from aggregated orders
for (oid, buyer), odata in order_summary.items():
    ord_amt = odata['amount']
    created_at = odata['date']
    territory = odata['territory']
    
    o = outlets[buyer]
    o['revenue'] += ord_amt
    o['orders'] += 1
    o['skus_set'].update(odata['skus'])
    if territory and not o['territory']:
        o['territory'] = territory
        
    if not o['first_order_date'] or created_at < o['first_order_date']:
        o['first_order_date'] = created_at
    if not o['last_order_date'] or created_at > o['last_order_date']:
        o['last_order_date'] = created_at
        
    o['order_dates_set'].add(created_at)
    
    d = days_ago(created_at)
    if d <= ACTIVE_DAYS:
        o['recent_revenue'] += ord_amt
        o['recent_orders'] += 1
    else:
        o['historical_revenue'] += ord_amt
        o['historical_orders'] += 1
        
    total_revenue += ord_amt

del order_summary # Free memory

# ─── 3. PROCESS VISITS ───────────────────────────────────────────────────────
print("\n[3/4] Processing visits...")
n_visits = 0
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        buyer = (r.get('department_id') or '').strip()
        if not buyer:
            continue
        created_at = (r.get('created_at') or '')[:10]
        if not is_valid_month(created_at):
            continue
            
        d = days_ago(created_at)
        o = outlets[buyer]
        o['total_visits'] += 1
        if not o['last_visit_date'] or created_at > o['last_visit_date']:
            o['last_visit_date'] = created_at
        if d <= ACTIVE_DAYS:
            o['recent_visits'] += 1
        if d <= AT_RISK_DAYS:
            o['churn_period_visits'] += 1
        n_visits += 1

print(f"  Valid visits: {n_visits:,} | Total Outlets Profiled: {len(outlets):,}")

# ─── 4. SEGMENTATION & ANALYTICS ─────────────────────────────────────────────
print("\n[4/4] Computing RFM segmentation & Churn analytics...")

segments = {s: {'count': 0, 'revenue': 0.0, 'aov_sum': 0.0, 'freq': 0.0, 'skus': 0.0}
            for s in ['Champions', 'Loyal Base', 'Potential', 'At-Risk', 'Lost']}

churned_buyers = 0
lost_revenue   = 0.0
churn_visit_gap   = 0
churn_service_gap = 0

silent_bleed_outlets = []
total_silent_bleed_lost = 0.0

churn_risk_outlets = []
total_risk_revenue = 0.0

red_flags = []

for buyer, o in outlets.items():
    freq = o['orders']
    rev  = o['revenue']
    aov  = rev / freq if freq > 0 else 0
    recency_days = days_ago(o['last_order_date'])
    sku_cnt = len(o['skus_set'])
    terr = o.get('territory') or 'National Retail'

    dept = dept_map.get(buyer, {})
    outlet_name = dept.get('name', '') or f"Outlet {buyer}"
    owner_name  = dept.get('owner', '')
    phone_no    = dept.get('phone', '')
    addr_str    = dept.get('address', '')

    # ── Red Flag: never ordered, but visited a lot ──────────────────────────
    if freq == 0:
        if o['total_visits'] > RED_FLAG_VISIT_COUNT:
            red_flags.append({
                'outlet': buyer, 'name': outlet_name, 'owner': owner_name, 'phone': phone_no, 'address': addr_str,
                'territory': terr, 'visits': o['total_visits'], 'last_visit': o['last_visit_date'],
                'historical_orders': 0
            })
        continue

    # ── RFM Segment Assignment ───────────────────────────────────────────────
    if recency_days <= ACTIVE_DAYS:
        if freq >= 10 and rev > 50000:
            segment = 'Champions'
        elif freq >= 4:
            segment = 'Loyal Base'
        else:
            segment = 'Potential'
    elif recency_days <= AT_RISK_DAYS:
        segment = 'At-Risk'
    else:
        segment = 'Lost'

    s = segments[segment]
    s['count']   += 1
    s['revenue'] += rev
    s['aov_sum'] += aov
    s['freq']    += freq
    s['skus']    += sku_cnt

    # ── Drop-Off / Churn Root Cause ──────────────────────────────────────────
    if segment == 'Lost':
        churned_buyers += 1
        lost_revenue   += rev
        if o['churn_period_visits'] == 0:
            churn_visit_gap += 1   # Never visited → Visit Gap
        else:
            churn_service_gap += 1 # Visited but still churned → Service Gap

    dept = dept_map.get(buyer, {})
    outlet_name = dept.get('name', '') or f"Outlet {buyer}"
    owner_name  = dept.get('owner', '')
    phone_no    = dept.get('phone', '')
    addr_str    = dept.get('address', '')

    # ── Silent Bleed Analysis ────────────────────────────────────────────────
    if segment in ['Champions', 'Loyal Base', 'Potential'] and o['historical_orders'] > 0 and o['recent_orders'] > 0:
        hist_aov = o['historical_revenue'] / o['historical_orders']
        rec_aov  = o['recent_revenue']     / o['recent_orders']
        if hist_aov > 500 and rec_aov < hist_aov * (1 - SILENT_BLEED_THRESHOLD):
            bleed = (hist_aov - rec_aov) * o['recent_orders']
            total_silent_bleed_lost += bleed
            silent_bleed_outlets.append({
                'outlet': buyer, 'name': outlet_name, 'owner': owner_name, 'phone': phone_no, 'address': addr_str, 'territory': terr,
                'hist_aov': round(hist_aov, 1), 'rec_aov': round(rec_aov, 1),
                'drop_pct': round((1 - rec_aov / hist_aov) * 100, 1),
                'lost_rev': round(bleed, 1)
            })

    # ── Churn Risk Prediction (2.0x-2.5x historical interval) ───────────────
    if freq >= 3 and o['first_order_date'] and o['last_order_date'] and o['first_order_date'] != o['last_order_date']:
        days_active = (datetime.strptime(o['last_order_date'], "%Y-%m-%d") -
                       datetime.strptime(o['first_order_date'], "%Y-%m-%d")).days
        if days_active > 0:
            avg_gap = days_active / (freq - 1)
            if avg_gap > 0 and recency_days > avg_gap * CHURN_RISK_MULTIPLIER:
                risk_level = "High" if recency_days > avg_gap * CHURN_HIGH_MULTIPLIER else "Medium"
                # The revenue at risk represents the expected revenue that would have occurred (expected monthly rate)
                expected_frequency = 30.0 / avg_gap if avg_gap > 0 else 1.0
                risk_rev = round(min(rev, aov * expected_frequency), 1)
                total_risk_revenue += risk_rev
                churn_risk_outlets.append({
                    'outlet': buyer, 'name': outlet_name, 'owner': owner_name, 'phone': phone_no, 'address': addr_str, 'territory': terr,
                    'avg_gap': round(avg_gap, 1), 'current_gap': recency_days,
                    'multiplier': round(recency_days / avg_gap, 2),
                    'risk_level': risk_level, 'rev_at_risk': risk_rev,
                    'segment': segment
                })

    # ── Red Flag: placed orders before but now >5 visits with 0 recent orders ─
    if o['recent_orders'] == 0 and o['total_visits'] > RED_FLAG_VISIT_COUNT and freq > 0:
        red_flags.append({
            'outlet': buyer, 'name': outlet_name, 'owner': owner_name, 'phone': phone_no, 'address': addr_str, 'territory': terr,
            'visits': o['total_visits'], 'last_visit': o['last_visit_date'],
            'historical_orders': freq
        })

# Finalize Segment Averages
for k, s in segments.items():
    c = s['count']
    if c > 0:
        s['aov']  = round(s['aov_sum'] / c, 1)
        s['freq'] = round(s['freq'] / c, 1)
        s['skus'] = round(s['skus'] / c, 1)
        s['rev_pct'] = round(s['revenue'] / total_revenue * 100, 1) if total_revenue > 0 else 0
        s['revenue'] = round(s['revenue'], 1)
    del s['aov_sum']

# Sort Tables
silent_bleed_outlets.sort(key=lambda x: -x['lost_rev'])
churn_risk_outlets.sort(key=lambda x: (-{'High': 2, 'Medium': 1}.get(x['risk_level'], 0), -x['rev_at_risk']))
red_flags.sort(key=lambda x: -x['visits'])

# Churn Risk Summary
churn_risk_high   = [r for r in churn_risk_outlets if r['risk_level'] == 'High']
churn_risk_medium = [r for r in churn_risk_outlets if r['risk_level'] == 'Medium']
churn_risk_total_rev = round(sum(r['rev_at_risk'] for r in churn_risk_outlets), 1)

# Risk by territory
risk_by_terr = defaultdict(lambda: {'high_rev': 0.0, 'med_rev': 0.0, 'count': 0, 'rev': 0.0})
for r in churn_risk_outlets:
    t = r['territory'] or 'National Retail'
    if r['risk_level'] == 'High':
        risk_by_terr[t]['high_rev'] += r['rev_at_risk']
    else:
        risk_by_terr[t]['med_rev'] += r['rev_at_risk']
    risk_by_terr[t]['rev'] += r['rev_at_risk']
    risk_by_terr[t]['count'] += 1

churn_risk_terr_list = []
for t, d in sorted(risk_by_terr.items(), key=lambda x: -x[1]['rev'])[:12]:
    churn_risk_terr_list.append({
        'territory': t,
        'count': d['count'],
        'rev': round(d['rev'], 1),
        'high_risk_rev': round(d['high_rev'], 1),
        'medium_risk_rev': round(d['med_rev'], 1),
        'total_risk_rev': round(d['rev'], 1)
    })

# Silent bleed by territory
bleed_by_terr = defaultdict(lambda: {'count': 0, 'lost': 0.0})
for b in silent_bleed_outlets:
    t = b['territory'] or 'National Retail'
    bleed_by_terr[t]['count'] += 1
    bleed_by_terr[t]['lost'] += b['lost_rev']

silent_bleed_terr_list = []
for t, d in sorted(bleed_by_terr.items(), key=lambda x: -x[1]['lost'])[:12]:
    silent_bleed_terr_list.append({
        'territory': t,
        'count': d['count'],
        'lost': round(d['lost'], 1)
    })

# Assemble Output
total_outlets_count = len(outlets)
active_outlets_count = sum(s['count'] for k, s in segments.items() if k != 'Lost')

summary_obj = {
    'total_outlets':        total_outlets_count,
    'total_active':         active_outlets_count,
    'active_outlets':        active_outlets_count,
    'churned_outlets':       churned_buyers,
    'total_revenue':         round(total_revenue, 1),
    'lost_revenue':          round(lost_revenue, 1),
    'churn_visit_gap':       churn_visit_gap,
    'churn_service_gap':     churn_service_gap,
    'silent_bleed_count':    len(silent_bleed_outlets),
    'silent_bleed_lost':     round(total_silent_bleed_lost, 1),
    'churn_risk_count':      len(churn_risk_outlets),
    'churn_risk_high_count': len(churn_risk_high),
    'churn_risk_med_count':  len(churn_risk_medium),
    'churn_risk_rev':        round(churn_risk_total_rev, 1),
    'churn_risk_revenue':    round(churn_risk_total_rev, 1),
    'red_flag_count':        len(red_flags),
    'red_flags_count':       len(red_flags)
}

dropoff_obj = {
    'total_lost': churned_buyers,
    'lost_revenue': round(lost_revenue, 1),
    'visit_gap': churn_visit_gap,
    'service_gap': churn_service_gap
}

churn_risk_summary = {
    'total_count': len(churn_risk_outlets),
    'high_count': len(churn_risk_high),
    'medium_count': len(churn_risk_medium),
    'total_rev': round(churn_risk_total_rev, 1),
    'by_territory': churn_risk_terr_list
}

# Silent bleed severity distribution (across all 28k+ silent_bleed_outlets)
bleed_severity_buckets = {'50-60%': 0, '60-70%': 0, '70-80%': 0, '80-90%': 0, '90%+': 0}
for b in silent_bleed_outlets:
    d = b['drop_pct']
    if d < 60: bleed_severity_buckets['50-60%'] += 1
    elif d < 70: bleed_severity_buckets['60-70%'] += 1
    elif d < 80: bleed_severity_buckets['70-80%'] += 1
    elif d < 90: bleed_severity_buckets['80-90%'] += 1
    else: bleed_severity_buckets['90%+'] += 1

silent_bleed_summary = {
    'total_count': len(silent_bleed_outlets),
    'total_lost': round(total_silent_bleed_lost, 1),
    'severity_buckets': bleed_severity_buckets,
    'by_territory': silent_bleed_terr_list
}

# Red flag visit distribution & territory breakdown (across all red_flags)
red_flag_visit_buckets = {'6-10': 0, '11-20': 0, '21-30': 0, '31-50': 0, '50+': 0}
red_flag_terr_map = defaultdict(int)
for f in red_flags:
    v = f['visits']
    if v <= 10: red_flag_visit_buckets['6–10'] += 1
    elif v <= 20: red_flag_visit_buckets['11–20'] += 1
    elif v <= 30: red_flag_visit_buckets['21–30'] += 1
    elif v <= 50: red_flag_visit_buckets['31–50'] += 1
    else: red_flag_visit_buckets['50+'] += 1
    t = f['territory'] or 'National Retail'
    red_flag_terr_map[t] += 1

red_flag_terr_list = [{'territory': t, 'count': c} for t, c in sorted(red_flag_terr_map.items(), key=lambda x: -x[1])[:12]]

red_flag_summary = {
    'total_count': len(red_flags),
    'visit_buckets': red_flag_visit_buckets,
    'by_territory': red_flag_terr_list
}

output_data = {
    'summary': summary_obj,
    'kpis': summary_obj,
    'rfm_segments': segments,
    'segments': segments,
    'dropoff': dropoff_obj,
    'top_risk_territories': churn_risk_terr_list,
    'churn_risk_summary': churn_risk_summary,
    'churn_risk': churn_risk_outlets[:300],
    'churn_risk_top': churn_risk_outlets[:300],
    'silent_bleed_summary': silent_bleed_summary,
    'silent_bleed': silent_bleed_outlets[:300],
    'silent_bleed_top': silent_bleed_outlets[:300],
    'red_flag_summary': red_flag_summary,
    'red_flags': red_flags[:200],
    'red_flags_top': red_flags[:200]
}

with open(r'e:\ITL FINAL ADV ANALYSIS\module3_data.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

with open(r'e:\ITL FINAL ADV ANALYSIS\module3_data.js', 'w', encoding='utf-8') as f:
    f.write('window.MODULE3_DATA = ' + json.dumps(output_data, ensure_ascii=False) + ';')

# Write complete CSV exports for Module 3
with open(r'e:\ITL FINAL ADV ANALYSIS\module3_churn_risk.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Outlet_ID', 'Outlet_Name', 'Owner_Name', 'Phone_Number', 'Address', 'Territory', 'RFM_Segment', 'Avg_Cycle_Days', 'Current_Gap_Days', 'Multiplier', 'Risk_Level', 'Revenue_At_Risk_BDT'])
    writer.writeheader()
    for r in churn_risk_outlets:
        writer.writerow({
            'Outlet_ID': r['outlet'], 'Outlet_Name': r.get('name',''), 'Owner_Name': r.get('owner',''),
            'Phone_Number': r.get('phone',''), 'Address': r.get('address',''), 'Territory': r['territory'],
            'RFM_Segment': r['segment'], 'Avg_Cycle_Days': r['avg_gap'], 'Current_Gap_Days': r['current_gap'],
            'Multiplier': r['multiplier'], 'Risk_Level': r['risk_level'], 'Revenue_At_Risk_BDT': r['rev_at_risk']
        })

with open(r'e:\ITL FINAL ADV ANALYSIS\module3_silent_bleed.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Outlet_ID', 'Outlet_Name', 'Owner_Name', 'Phone_Number', 'Address', 'Territory', 'Historical_AOV_BDT', 'Recent_AOV_BDT', 'AOV_Drop_Pct', 'Wallet_Lost_BDT'])
    writer.writeheader()
    for b in silent_bleed_outlets:
        writer.writerow({
            'Outlet_ID': b['outlet'], 'Outlet_Name': b.get('name',''), 'Owner_Name': b.get('owner',''),
            'Phone_Number': b.get('phone',''), 'Address': b.get('address',''), 'Territory': b['territory'],
            'Historical_AOV_BDT': b['hist_aov'], 'Recent_AOV_BDT': b['rec_aov'],
            'AOV_Drop_Pct': b['drop_pct'], 'Wallet_Lost_BDT': b['lost_rev']
        })

with open(r'e:\ITL FINAL ADV ANALYSIS\module3_red_flags.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Outlet_ID', 'Outlet_Name', 'Owner_Name', 'Phone_Number', 'Address', 'Territory', 'Total_Visits', 'Last_Visit_Date', 'Historical_Orders'])
    writer.writeheader()
    for rf in red_flags:
        writer.writerow({
            'Outlet_ID': rf['outlet'], 'Outlet_Name': rf.get('name',''), 'Owner_Name': rf.get('owner',''),
            'Phone_Number': rf.get('phone',''), 'Address': rf.get('address',''), 'Territory': rf['territory'],
            'Total_Visits': rf['visits'], 'Last_Visit_Date': rf['last_visit'], 'Historical_Orders': rf['historical_orders']
        })

print("\n✓ SUCCESS: Module 3 data pipeline regenerated without outliers!")
print(f"  → Total Outlets: {total_outlets_count:,} | Active Outlets: {active_outlets_count:,}")
print(f"  → Total Revenue: ৳ {total_revenue:,.2f}")
print(f"  → Churn Risk Revenue: ৳ {churn_risk_total_rev:,.2f} ({len(churn_risk_outlets):,} outlets)")
print(f"  → Silent Bleed Lost: ৳ {total_silent_bleed_lost:,.2f} ({len(silent_bleed_outlets):,} outlets)")
