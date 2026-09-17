"""
Advanced Market Basket Analysis:
Computes Pairwise (A -> B) and Triplet (A + B -> C) Association Rules
with both Volume (Frequency) and Lift Rankings, including rich Tea combinations.
"""
import csv, json, sys, time
from collections import defaultdict
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8')

print("Loading orders from itl_orders.csv...")
t0 = time.time()

products = {}          # sku -> {name, brand, cat}
order_items = defaultdict(set)   # order_id -> set of skus

with open(r'e:\ITL FINAL ADV ANALYSIS\itl_orders.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sku = r.get('product_sku', '')
        name = r.get('product_name', '')
        brand = r.get('product_brand_name', '')
        cat = r.get('product_category_name', '')
        amt = float(r.get('amount', '0') or 0)
        oid = r.get('order_id', '')
        status = r.get('order_status', '')

        if status == 'cancelled' or amt > 500000:
            continue

        if sku not in products:
            products[sku] = {'name': name, 'brand': brand, 'cat': cat}

        order_items[oid].add(sku)

N_orders = len(order_items)
print(f"Loaded {N_orders:,} valid orders across {len(products)} SKUs in {time.time()-t0:.2f}s")

# 1. Item support
item_support = defaultdict(int)
for oid, skus in order_items.items():
    for sku in skus:
        item_support[sku] += 1

# 2. Pair co-occurrences
pair_count = defaultdict(int)
triplet_count = defaultdict(int)

for oid, skus in order_items.items():
    skus_list = sorted(skus)
    k = len(skus_list)
    if k >= 2:
        for a, b in combinations(skus_list, 2):
            pair_count[(a, b)] += 1
    if k >= 3:
        # Only take combinations of up to top 60 frequent SKUs or limit combinations if order is large
        if k > 15:
            # Sort by item support to avoid combinatorial explosion on rare bulk orders
            skus_list = sorted(skus_list, key=lambda s: -item_support[s])[:15]
            skus_list.sort()
        for a, b, c in combinations(skus_list, 3):
            triplet_count[(a, b, c)] += 1

print(f"Unique pairs: {len(pair_count):,} | Unique triplets: {len(triplet_count):,}")

# 3. Compute Pairwise Rules (A -> B)
pairs_list = []
for (a, b), co_count in pair_count.items():
    if co_count < 30:
        continue
    support_ab = co_count / N_orders
    conf_ab = co_count / item_support[a] if item_support[a] > 0 else 0
    conf_ba = co_count / item_support[b] if item_support[b] > 0 else 0
    
    supp_a = item_support[a] / N_orders
    supp_b = item_support[b] / N_orders
    lift = support_ab / (supp_a * supp_b) if (supp_a * supp_b) > 0 else 0

    p_a = products.get(a, {})
    p_b = products.get(b, {})

    pairs_list.append({
        'sku_a': a, 'name_a': p_a.get('name', a), 'brand_a': p_a.get('brand', ''), 'cat_a': p_a.get('cat', ''),
        'sku_b': b, 'name_b': p_b.get('name', b), 'brand_b': p_b.get('brand', ''), 'cat_b': p_b.get('cat', ''),
        'co_count': co_count,
        'support': round(support_ab * 100, 4),
        'confidence_ab': round(conf_ab * 100, 2),
        'confidence_ba': round(conf_ba * 100, 2),
        'lift': round(lift, 3)
    })

print(f"Computed {len(pairs_list):,} qualified pairs (co_count >= 30)")

# 4. Compute Triplet Rules (A + B -> C)
triplets_list = []
for (a, b, c), co_count in triplet_count.items():
    if co_count < 20:
        continue
    
    # Try all 3 antecedents
    perms = [
        (a, b, c), # (a,b) -> c
        (a, c, b), # (a,c) -> b
        (b, c, a)  # (b,c) -> a
    ]
    
    for ant1, ant2, cons in perms:
        pair_ab = (min(ant1, ant2), max(ant1, ant2))
        count_ab = pair_count.get(pair_ab, 0)
        if count_ab < 25:
            continue
        
        conf = co_count / count_ab
        supp_triplet = co_count / N_orders
        supp_cons = item_support[cons] / N_orders
        supp_pair = count_ab / N_orders
        
        lift = supp_triplet / (supp_pair * supp_cons) if (supp_pair * supp_cons) > 0 else 0
        
        p_1 = products.get(ant1, {})
        p_2 = products.get(ant2, {})
        p_c = products.get(cons, {})
        
        triplets_list.append({
            'sku_a': ant1, 'name_a': p_1.get('name', ant1), 'brand_a': p_1.get('brand', ''), 'cat_a': p_1.get('cat', ''),
            'sku_b': ant2, 'name_b': p_2.get('name', ant2), 'brand_b': p_2.get('brand', ''), 'cat_b': p_2.get('cat', ''),
            'sku_c': cons, 'name_c': p_c.get('name', cons), 'brand_c': p_c.get('brand', ''), 'cat_c': p_c.get('cat', ''),
            'co_count': co_count,
            'pair_count': count_ab,
            'support': round(supp_triplet * 100, 4),
            'confidence': round(conf * 100, 2),
            'lift': round(lift, 3)
        })

print(f"Computed {len(triplets_list):,} qualified triplet rules")

# Filter sets
# Pairs by volume
pairs_by_volume = sorted(pairs_list, key=lambda x: -x['co_count'])[:50]
# Pairs by lift
pairs_by_lift = sorted(pairs_list, key=lambda x: -x['lift'])[:50]
# Tea pairs (at least one is Tea)
tea_pairs = [p for p in pairs_list if p['cat_a'] == 'Tea' or p['cat_b'] == 'Tea']
tea_pairs = sorted(tea_pairs, key=lambda x: -x['co_count'])[:50]

# Triplets by volume
triplets_by_volume = sorted(triplets_list, key=lambda x: -x['co_count'])[:50]
# Triplets by lift
triplets_by_lift = sorted(triplets_list, key=lambda x: -x['lift'])[:50]
# Tea triplets
tea_triplets = [t for t in triplets_list if 'Tea' in (t['cat_a'], t['cat_b'], t['cat_c'])]
tea_triplets = sorted(tea_triplets, key=lambda x: -x['co_count'])[:50]

print(f"Top volume pair: {pairs_by_volume[0]['name_a']} + {pairs_by_volume[0]['name_b']} ({pairs_by_volume[0]['co_count']:,} orders)")
print(f"Top volume triplet: {triplets_by_volume[0]['name_a']} + {triplets_by_volume[0]['name_b']} -> {triplets_by_volume[0]['name_c']} ({triplets_by_volume[0]['co_count']:,} orders)")

# Update module2_data.json
with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.json', 'r', encoding='utf-8') as f:
    m2 = json.load(f)

m2['basket']['top_pairs'] = pairs_by_lift[:30] # for legacy compatibility
m2['basket']['pairs_by_volume'] = pairs_by_volume
m2['basket']['pairs_by_lift'] = pairs_by_lift
m2['basket']['tea_pairs'] = tea_pairs
m2['basket']['triplets_by_volume'] = triplets_by_volume
m2['basket']['triplets_by_lift'] = triplets_by_lift
m2['basket']['tea_triplets'] = tea_triplets
m2['basket']['all_pairs_sample'] = pairs_by_volume[:100]

with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.json', 'w', encoding='utf-8') as f:
    json.dump(m2, f, ensure_ascii=False, indent=2)

with open(r'e:\ITL FINAL ADV ANALYSIS\module2_data.js', 'w', encoding='utf-8') as f:
    f.write('const D = ' + json.dumps(m2, ensure_ascii=False, indent=2) + ';\n')

print("Successfully updated module2_data.json and module2_data.js with Advanced Market Basket pairs & triplets!")
