import csv
import json
import sys
from collections import defaultdict
from datetime import datetime

csv.field_size_limit(2147483647)
sys.stdout.reconfigure(encoding='utf-8')

print("=== FAST REBUILD FOR MODULE 3 DATA ===")

ACTIVE_DAYS = 60
AT_RISK_DAYS = 120
OUTLIER_THRESHOLD = 500000
SILENT_BLEED_THRESHOLD = 0.50
RED_FLAG_VISIT_COUNT = 5
CHURN_RISK_MULTIPLIER = 2.0
CHURN_HIGH_MULTIPLIER = 2.5
MAX_DATE = datetime(2026, 8, 31)

def days_ago(date_str):
    if not date_str: return 9999
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

# 1. Build territory lookup map
print("1. Reading territory names...")
territory_name_map = {}
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sdt = (r.get('seller_department_territory') or '').strip()
        sdn = (r.get('seller_department_name') or '').strip()
        if sdt and sdn and sdt not in territory_name_map:
            territory_name_map[sdt] = sdn

# 2. Process orders
print("2. Processing orders...")
outlets = defaultdict(lambda: {
    'orders': 0,
    'revenue': 0.0,
    'first_order_date': None,
    'last_order_date': None,
    'recent_revenue': 0.0,
    'recent_orders': 0,
    'historical_revenue': 0.0,
    'historical_orders': 0,
    'skus_set': set(),
    'territory': '',
    'total_visits': 0,
    'last_visit_date': None,
    'recent_visits': 0,
    'churn_period_visits': 0
})

total_revenue = 0.0
n_lines = 0

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

        territory_raw = (r.get('seller_department_territory') or '').strip()
        territory = territory_name_map.get(territory_raw, territory_raw) or 'National Retail'
        sku = (r.get('product_sku') or '').strip()

        o = outlets[buyer]
        o['revenue'] += amt
        o['orders'] += 1
        if sku:
            o['skus_set'].add(sku)
        if territory and not o['territory']:
            o['territory'] = territory

        if not o['first_order_date'] or created_at < o['first_order_date']:
            o['first_order_date'] = created_at
        if not o['last_order_date'] or created_at > o['last_order_date']:
            o['last_order_date'] = created_at

        d = days_ago(created_at)
        if d <= ACTIVE_DAYS:
            o['recent_revenue'] += amt
            o['recent_orders'] += 1
        else:
            o['historical_revenue'] += amt
            o['historical_orders'] += 1

        total_revenue += amt
        n_lines += 1

print(f"Processed {n_lines:,} lines. Total outlets: {len(outlets):,}")

# 3. Process visits
print("3. Processing visits...")
n_visits = 0
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_checkings.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        buyer = (r.get('department_id') or '').strip()
        if not buyer: continue
        created_at = (r.get('created_at') or '')[:10]
        if not is_valid_month(created_at): continue
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

print(f"Processed {n_visits:,} visits.")

# 4. Compute RFM & Churn
print("4. Computing RFM segments and churn...")
segments = {s: {'count': 0, 'revenue': 0.0, 'aov_sum': 0.0, 'freq': 0.0, 'skus': 0.0}
            for s in ['Champions', 'Loyal Base', 'Potential', 'At-Risk', 'Lost']}

churned_buyers = 0
lost_revenue = 0.0
churn_visit_gap = 0
churn_service_gap = 0

silent_bleed_outlets = []
total_silent_bleed_lost = 0.0

churn_risk_outlets = []
total_risk_revenue = 0.0

red_flags = []

for buyer, o in outlets.items():
    freq = o['orders']
    rev = o['revenue']
    aov = rev / freq if freq > 0 else 0
    recency_days = days_ago(o['last_order_date'])
    sku_cnt = len(o['skus_set'])
    terr = o.get('territory') or 'National Retail'

    if freq == 0:
        if o['total_visits'] > RED_FLAG_VISIT_COUNT:
            red_flags.append({
                'outlet': buyer, 'territory': terr,
                'visits': o['total_visits'], 'last_visit': o['last_visit_date']
            })
        continue

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
    s['count'] += 1
    s['revenue'] += rev
    s['aov_sum'] += aov
    s['freq'] += freq
    s['skus'] += sku_cnt

    if segment in ['At-Risk', 'Lost']:
        churned_buyers += 1
        lost_revenue += rev
        if o['churn_period_visits'] == 0:
            churn_visit_gap += 1
        else:
            churn_service_gap += 1

    # Silent Bleed
    if segment in ['Champions', 'Loyal Base', 'Potential'] and o['historical_orders'] > 0 and o['recent_orders'] > 0:
        hist_aov = o['historical_revenue'] / o['historical_orders']
        rec_aov = o['recent_revenue'] / o['recent_orders']
        if hist_aov > 500 and rec_aov < hist_aov * (1 - SILENT_BLEED_THRESHOLD):
            bleed = (hist_aov - rec_aov) * o['recent_orders']
            total_silent_bleed_lost += bleed
            silent_bleed_outlets.append({
                'outlet': buyer, 'territory': terr,
                'hist_aov': round(hist_aov, 1), 'rec_aov': round(rec_aov, 1),
                'drop_pct': round((1 - rec_aov / hist_aov) * 100, 1),
                'lost_rev': round(bleed, 1)
            })

    # Churn Risk
    if freq >= 3 and o['first_order_date'] and o['last_order_date'] and o['first_order_date'] != o['last_order_date']:
        try:
            days_active = (datetime.strptime(o['last_order_date'], "%Y-%m-%d") -
                           datetime.strptime(o['first_order_date'], "%Y-%m-%d")).days
            if days_active > 0:
                avg_gap = days_active / (freq - 1)
                if avg_gap > 0 and recency_days > avg_gap * CHURN_RISK_MULTIPLIER:
                    risk_level = "High" if recency_days > avg_gap * CHURN_HIGH_MULTIPLIER else "Medium"
                    expected_frequency = 30.0 / avg_gap if avg_gap > 0 else 1.0
                    risk_rev = round(min(rev, aov * expected_frequency), 1)
                    total_risk_revenue += risk_rev
                    churn_risk_outlets.append({
                        'outlet': buyer, 'territory': terr,
                        'avg_gap': round(avg_gap, 1), 'current_gap': recency_days,
                        'multiplier': round(recency_days / avg_gap, 2),
                        'risk_level': risk_level, 'rev_at_risk': risk_rev,
                        'segment': segment
                    })
        except:
            pass

    if o['recent_orders'] == 0 and o['total_visits'] > RED_FLAG_VISIT_COUNT and freq > 0:
        red_flags.append({
            'outlet': buyer, 'territory': terr,
            'visits': o['total_visits'], 'last_visit': o['last_visit_date'],
            'historical_orders': freq
        })

# Finalize segments
for k, s in segments.items():
    c = s['count']
    if c > 0:
        s['aov'] = round(s['aov_sum'] / c, 1)
        s['freq'] = round(s['freq'] / c, 1)
        s['skus'] = round(s['skus'] / c, 1)
        s['rev_pct'] = round(s['revenue'] / total_revenue * 100, 1) if total_revenue > 0 else 0
        s['revenue'] = round(s['revenue'], 1)
    del s['aov_sum']

silent_bleed_outlets.sort(key=lambda x: -x['lost_rev'])
churn_risk_outlets.sort(key=lambda x: (-{'High': 2, 'Medium': 1}.get(x['risk_level'], 0), -x['rev_at_risk']))
red_flags.sort(key=lambda x: -x['visits'])

churn_risk_high = [r for r in churn_risk_outlets if r['risk_level'] == 'High']
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

total_outlets_count = len(outlets)
active_outlets_count = sum(s['count'] for k, s in segments.items() if k != 'Lost')

kpi_summary = {
    'total_outlets': total_outlets_count,
    'total_active': active_outlets_count,
    'active_outlets': active_outlets_count,
    'churned_outlets': churned_buyers,
    'total_revenue': round(total_revenue, 1),
    'lost_revenue': round(lost_revenue, 1),
    'churn_visit_gap': churn_visit_gap,
    'churn_service_gap': churn_service_gap,
    'silent_bleed_count': len(silent_bleed_outlets),
    'silent_bleed_lost': round(total_silent_bleed_lost, 1),
    'churn_risk_count': len(churn_risk_outlets),
    'churn_risk_high_count': len(churn_risk_high),
    'churn_risk_med_count': len(churn_risk_medium),
    'churn_risk_rev': round(churn_risk_total_rev, 1),
    'churn_risk_revenue': round(churn_risk_total_rev, 1),
    'red_flag_count': len(red_flags),
    'red_flags_count': len(red_flags)
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

silent_bleed_summary = {
    'total_count': len(silent_bleed_outlets),
    'total_lost': round(total_silent_bleed_lost, 1),
    'by_territory': silent_bleed_terr_list
}

red_flag_summary = {
    'total_count': len(red_flags)
}

output_data = {
    'summary': kpi_summary,
    'kpis': kpi_summary,
    'rfm_segments': segments,
    'segments': segments,
    'dropoff': dropoff_obj,
    'churn_risk_summary': churn_risk_summary,
    'churn_risk': churn_risk_outlets[:300],
    'silent_bleed_summary': silent_bleed_summary,
    'silent_bleed': silent_bleed_outlets[:300],
    'red_flag_summary': red_flag_summary,
    'red_flags': red_flags[:200]
}

with open(r'e:\ITL FINAL ADV ANALYSIS\module3_data.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

with open(r'e:\ITL FINAL ADV ANALYSIS\module3_data.js', 'w', encoding='utf-8') as f:
    f.write('window.MODULE3_DATA = ' + json.dumps(output_data, ensure_ascii=False) + ';')

print("✓ Rebuild complete! Successfully populated all objects matching HTML bindings.")
