"""
Generates complete Outlet Details CSV files for all 5 RFM Segments:
- itl_rfm_champions_outlets.csv
- itl_rfm_loyal_base_outlets.csv
- itl_rfm_potential_outlets.csv
- itl_rfm_at_risk_outlets.csv
- itl_rfm_lost_outlets.csv
- itl_all_rfm_outlets.csv
"""
import csv, json, sys, time
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

MAX_DATE = datetime(2026, 8, 31)
ACTIVE_DAYS = 30
AT_RISK_DAYS = 60
OUTLIER_THRESHOLD = 500000

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

t0 = time.time()
print("1. Loading outlet master catalog from itl_dept.csv...")
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

print(f"  Mapped {len(dept_map):,} dept records in {time.time()-t0:.2f}s")

print("2. Aggregating orders from itl_orders.csv...")
t1 = time.time()
territory_map = {}
outlets = defaultdict(lambda: {
    'orders': 0,
    'revenue': 0.0,
    'first_order_date': None,
    'last_order_date': None,
    'skus_set': set(),
    'territory': ''
})

order_summary = defaultdict(lambda: {'buyer': '', 'date': '', 'amount': 0.0, 'territory': '', 'skus': set()})

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
        territory = (r.get('seller_department_territory') or '').strip()
        sdn = (r.get('seller_department_name') or '').strip()
        if territory and sdn and territory not in territory_map:
            territory_map[territory] = sdn

        sku = (r.get('product_sku') or '').strip()

        ord_key = (oid, buyer) if oid else (f"no_id_{len(order_summary)}", buyer)
        order_summary[ord_key]['buyer'] = buyer
        order_summary[ord_key]['date'] = created_at
        order_summary[ord_key]['amount'] += amt
        if territory: order_summary[ord_key]['territory'] = territory
        if sku: order_summary[ord_key]['skus'].add(sku)

print(f"  Aggregated {len(order_summary):,} unique orders in {time.time()-t1:.2f}s")

for (oid, buyer), odata in order_summary.items():
    o = outlets[buyer]
    o['revenue'] += odata['amount']
    o['orders'] += 1
    o['skus_set'].update(odata['skus'])
    t_raw = odata['territory']
    if t_raw and not o['territory']:
        o['territory'] = territory_map.get(t_raw, t_raw)
    
    created_at = odata['date']
    if not o['first_order_date'] or created_at < o['first_order_date']:
        o['first_order_date'] = created_at
    if not o['last_order_date'] or created_at > o['last_order_date']:
        o['last_order_date'] = created_at

del order_summary

print(f"3. Classifying {len(outlets):,} outlets into 5 RFM segments...")
segment_rows = {
    'Champions': [],
    'Loyal Base': [],
    'Potential': [],
    'At-Risk': [],
    'Lost': []
}
all_rows = []

headers = [
    'Outlet_ID', 'Outlet_Name', 'Owner_Name', 'Phone_Number', 'Address',
    'Territory', 'RFM_Segment', 'Total_Revenue_BDT', 'Total_Orders',
    'Avg_Order_Value_BDT', 'Unique_SKUs', 'Last_Order_Date', 'Recency_Days'
]

for buyer, o in outlets.items():
    freq = o['orders']
    rev = o['revenue']
    aov = rev / freq if freq > 0 else 0
    recency = days_ago(o['last_order_date'])
    sku_cnt = len(o['skus_set'])
    terr = o.get('territory') or 'National Retail'
    
    dept = dept_map.get(buyer, {})
    name = dept.get('name', '') or f"Outlet {buyer}"
    owner = dept.get('owner', '')
    phone = dept.get('phone', '')
    addr = dept.get('address', '')

    if recency <= ACTIVE_DAYS:
        if freq >= 10 and rev > 50000:
            seg = 'Champions'
        elif freq >= 4:
            seg = 'Loyal Base'
        else:
            seg = 'Potential'
    elif recency <= AT_RISK_DAYS:
        seg = 'At-Risk'
    else:
        seg = 'Lost'

    row = {
        'Outlet_ID': buyer,
        'Outlet_Name': name,
        'Owner_Name': owner,
        'Phone_Number': phone,
        'Address': addr,
        'Territory': terr,
        'RFM_Segment': seg,
        'Total_Revenue_BDT': round(rev, 2),
        'Total_Orders': freq,
        'Avg_Order_Value_BDT': round(aov, 2),
        'Unique_SKUs': sku_cnt,
        'Last_Order_Date': o['last_order_date'] or '',
        'Recency_Days': recency
    }
    segment_rows[seg].append(row)
    all_rows.append(row)

file_map = {
    'Champions': r'e:\ITL FINAL ADV ANALYSIS\itl_rfm_champions_outlets.csv',
    'Loyal Base': r'e:\ITL FINAL ADV ANALYSIS\itl_rfm_loyal_base_outlets.csv',
    'Potential': r'e:\ITL FINAL ADV ANALYSIS\itl_rfm_potential_outlets.csv',
    'At-Risk': r'e:\ITL FINAL ADV ANALYSIS\itl_rfm_at_risk_outlets.csv',
    'Lost': r'e:\ITL FINAL ADV ANALYSIS\itl_rfm_lost_outlets.csv'
}

print("4. Writing CSV files...")
for seg, rows in segment_rows.items():
    filepath = file_map[seg]
    rows.sort(key=lambda x: -x['Total_Revenue_BDT'])
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ Written {len(rows):,} {seg} outlets to {filepath}")

all_rows.sort(key=lambda x: -x['Total_Revenue_BDT'])
all_path = r'e:\ITL FINAL ADV ANALYSIS\itl_all_rfm_outlets.csv'
with open(all_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(all_rows)
print(f"  ✓ Written {len(all_rows):,} total outlets to {all_path}")

print(f"\n🎉 All RFM segment CSV exports generated in {time.time()-t0:.2f}s!")
