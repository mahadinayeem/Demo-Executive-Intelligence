import csv, sys, json
sys.stdout.reconfigure(encoding='utf-8')

prods = {}
total = 0

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        total += 1
        sku = r.get('product_sku','')
        name = r.get('product_name','')
        brand = r.get('product_brand_name','')
        cat = r.get('product_category_name','')
        amt = float(r.get('amount','0') or 0)
        qty = float(r.get('order_qty','0') or 0)
        oid = r.get('order_id','')
        buyer = r.get('buyer_department_code','')
        status = r.get('order_status','')
        territory = r.get('seller_department_territory','')
        
        if sku not in prods:
            prods[sku] = {'name': name, 'brand': brand, 'cat': cat, 'revenue': 0, 'qty': 0, 'order_ids': set(), 'buyers': set()}
        prods[sku]['revenue'] += amt
        prods[sku]['qty'] += qty
        prods[sku]['order_ids'].add(oid)
        prods[sku]['buyers'].add(buyer)

print(f'Total rows: {total}')
print(f'Unique SKUs: {len(prods)}')

# Save product profile
out = []
for sku, d in prods.items():
    out.append({
        'sku': sku,
        'name': d['name'],
        'brand': d['brand'],
        'category': d['cat'],
        'revenue': round(d['revenue'],2),
        'qty': d['qty'],
        'order_count': len(d['order_ids']),
        'buyer_count': len(d['buyers'])
    })

out.sort(key=lambda x: -x['revenue'])

# Write CSV
with open(r'e:\ITL FINAL ADV ANALYSIS\product_profile.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=['sku','name','brand','category','revenue','qty','order_count','buyer_count'])
    w.writeheader()
    w.writerows(out)

print('Top 20 by revenue:')
for p in out[:20]:
    print(f"{p['sku']} | {p['name'][:40]} | {p['brand'][:20]} | {p['category']} | Rev={p['revenue']:.0f} | Orders={p['order_count']} | Buyers={p['buyer_count']}")

print('\nTotal revenue:', sum(p['revenue'] for p in out))
