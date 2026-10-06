"""
Generates complete Outlet Tier Details (Platinum, Gold, Silver, Bronze)
with Outlet Code, Name, Owner Name, Phone, Address, Territory, Revenue, Orders, SKUs, and Tier.
Exports full CSV files for each tier and embeds top tier samples into module2_data.json.
"""
import csv, json, sys, time
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

t0 = time.time()
print("1. Loading outlet master catalog from itl_dept.csv...")
dept_map = {}
with open(r'e:\ITL FINAL ADV ANALYSIS\itl_dept.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        c = r.get('code', '').strip()
        i = r.get('id', '').strip()
        name = r.get('name', '').strip()
        owner = r.get('owner_name', '').strip()
        phone = r.get('phone_no', '').strip()
        addr = r.get('address', '').strip()
        record = {'name': name, 'owner': owner, 'phone': phone, 'address': addr}
        if c: dept_map[c] = record
        if i and i not in dept_map: dept_map[i] = record

print(f"Mapped {len(dept_map):,} dept records in {time.time()-t0:.2f}s")

print("2. Aggregating outlet sales from itl_orders.csv...")
t1 = time.time()
outlet_revenue = defaultdict(float)
outlet_orders = defaultdict(set)
outlet_skus = defaultdict(set)
outlet_territory = {}

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        status = r.get('order_status', '')
        amt = float(r.get('amount', '0') or 0)
        if status == 'cancelled' or amt > 500000:
            continue
        
        buyer = r.get('buyer_department_code', '').strip()
        oid = r.get('order_id', '').strip()
        sku = r.get('product_sku', '').strip()
        territory = r.get('seller_department_territory', '').strip()

        if not buyer:
            continue

        outlet_revenue[buyer] += amt
        outlet_orders[buyer].add(oid)
        outlet_skus[buyer].add(sku)
        if buyer not in outlet_territory and territory:
            outlet_territory[buyer] = territory

print(f"Aggregated {len(outlet_revenue):,} active outlets in {time.time()-t1:.2f}s")

print("3. Classifying outlet tiers (Quartiles: Platinum, Gold, Silver, Bronze)...")
outlet_list = []
total_rev = sum(outlet_revenue.values())

for buyer, rev in outlet_revenue.items():
    n_orders = len(outlet_orders[buyer])
    n_skus = len(outlet_skus[buyer])
    info = dept_map.get(buyer, {})
    outlet_list.append({
        'code': buyer,
        'name': info.get('name', f"Outlet {buyer}"),
        'owner': info.get('owner', ''),
        'phone': info.get('phone', ''),
        'address': info.get('address', ''),
        'territory': outlet_territory.get(buyer, ''),
        'revenue': round(rev, 2),
        'orders': n_orders,
        'sku_count': n_skus,
        'avg_order_value': round(rev / n_orders, 2) if n_orders > 0 else 0
    })

# Sort by revenue descending
outlet_list.sort(key=lambda x: -x['revenue'])

# Classify using Industry-Standard FMCG Business Criteria
print("3. Classifying outlet tiers using FMCG Business Thresholds (>=50k, 15k-50k, 5k-15k, <5k)...")
for o in outlet_list:
    rev = o['revenue']
    if rev >= 50000:
        o['tier'] = 'Platinum'
    elif rev >= 15000:
        o['tier'] = 'Gold'
    elif rev >= 5000:
        o['tier'] = 'Silver'
    else:
        o['tier'] = 'Bronze'

# 4. Writing individual and combined CSVs
print("4. Writing full CSV files for all tiers...")
tier_groups = defaultdict(list)
for o in outlet_list:
    tier_groups[o['tier']].append(o)

tier_criteria_map = {
    'Platinum': '4-Month Revenue >= BDT 50,000 (>=৳12.5k/mo)',
    'Gold':     '4-Month Revenue BDT 15,000 - 50,000 (৳3.75k-12.5k/mo)',
    'Silver':   '4-Month Revenue BDT 5,000 - 15,000 (৳1.25k-3.75k/mo)',
    'Bronze':   '4-Month Revenue < BDT 5,000 (<৳1.25k/mo)'
}

for tier_name in ['Platinum', 'Gold', 'Silver', 'Bronze']:
    for base_dir in [r'e:\ITL FINAL ADV ANALYSIS', r'd:\ITL FINAL ADV ANALYSIS', '.']:
        try:
            filename = f"{base_dir}\\itl_outlets_{tier_name.lower()}_tier.csv"
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Rank_In_Tier", "Outlet_Code", "Outlet_Name", "Owner_Name", "Phone_Number", 
                    "Address", "Territory", "Tier", "Tier_Criteria", "Total_Revenue_BDT", "Total_Orders", 
                    "Unique_SKUs_Bought", "Avg_Order_Value_BDT"
                ])
                for idx, o in enumerate(tier_groups[tier_name]):
                    writer.writerow([
                        idx + 1, o['code'], o['name'], o['owner'], o['phone'],
                        o['address'], o['territory'], o['tier'], tier_criteria_map[tier_name], o['revenue'], o['orders'],
                        o['sku_count'], o['avg_order_value']
                    ])
            print(f"  Saved: {filename} ({len(tier_groups[tier_name]):,} outlets)")
        except Exception as err:
            pass

# Combined all outlets CSV
for base_dir in [r'e:\ITL FINAL ADV ANALYSIS', r'd:\ITL FINAL ADV ANALYSIS', '.']:
    try:
        all_filename = f"{base_dir}\\itl_all_outlets_by_tier.csv"
        with open(all_filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Overall_Rank", "Outlet_Code", "Outlet_Name", "Owner_Name", "Phone_Number", 
                "Address", "Territory", "Tier", "Tier_Criteria", "Total_Revenue_BDT", "Total_Orders", 
                "Unique_SKUs_Bought", "Avg_Order_Value_BDT"
            ])
            for idx, o in enumerate(outlet_list):
                writer.writerow([
                    idx + 1, o['code'], o['name'], o['owner'], o['phone'],
                    o['address'], o['territory'], o['tier'], tier_criteria_map[o['tier']], o['revenue'], o['orders'],
                    o['sku_count'], o['avg_order_value']
                ])
        print(f"  Saved: {all_filename} ({len(outlet_list):,} outlets)")
    except Exception as err:
        pass

# 5. Update module2_data.json with tier samples and full tier stats
print("5. Updating module2_data.json with sample top outlets for each tier...")
for base_dir in [r'e:\ITL FINAL ADV ANALYSIS', r'd:\ITL FINAL ADV ANALYSIS', '.']:
    try:
        json_path = f"{base_dir}\\module2_data.json"
        js_path = f"{base_dir}\\module2_data.js"
        with open(json_path, 'r', encoding='utf-8') as f:
            m2 = json.load(f)

        m2['tier_outlets_sample'] = {
            'Platinum': tier_groups['Platinum'][:100],
            'Gold': tier_groups['Gold'][:100],
            'Silver': tier_groups['Silver'][:100],
            'Bronze': tier_groups['Bronze'][:100]
        }

        tier_summary = []
        for t in ['Platinum', 'Gold', 'Silver', 'Bronze']:
            grp = tier_groups[t]
            t_rev = sum(x['revenue'] for x in grp)
            tier_summary.append({
                'tier': t,
                'criteria': tier_criteria_map[t],
                'outlet_count': len(grp),
                'revenue': round(t_rev, 2),
                'revenue_share': round(t_rev / total_rev * 100, 2),
                'avg_revenue': round(t_rev / len(grp), 2) if grp else 0,
                'avg_orders': round(sum(x['orders'] for x in grp) / len(grp), 1) if grp else 0,
                'avg_skus': round(sum(x['sku_count'] for x in grp) / len(grp), 1) if grp else 0,
                'download_file': f"itl_outlets_{t.lower()}_tier.csv"
            })

        m2['tiers'] = tier_summary

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(m2, f, ensure_ascii=False, indent=2)

        with open(js_path, 'w', encoding='utf-8') as f:
            f.write('window.MODULE2_DATA = ' + json.dumps(m2, ensure_ascii=False) + ';\n')
        print(f"  Updated JSON/JS in: {base_dir}")
    except Exception as err:
        pass

print("All tier exports and module2_data files updated successfully!")
