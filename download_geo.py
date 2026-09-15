import urllib.request, json, sys

urls = [
    'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_BGD_1.json',
    'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/bangladesh-divisions.geojson',
    'https://raw.githubusercontent.com/deldersveld/topojson/master/countries/bangladesh/bangladesh-divisions.json',
    'https://raw.githubusercontent.com/ArifSanaworker/bangladesh-geojson/main/bd-divisions.geojson',
    'https://raw.githubusercontent.com/jbkunst/highcharter/master/inst/extdata/bangladesh-geojson/bd-divisions.json',
    'https://raw.githubusercontent.com/nushaine/bangladesh-divisions/main/bd_divisions.geojson',
    'https://raw.githubusercontent.com/cigerxwinmern/bangladesh-geojson/master/bd-divisions.geojson',
    'https://data.humdata.org/dataset/4b5e7d8d-2c0f-482f-8bfc-3ef1ae3a17c5/resource/a8d3c5db-92fa-449c-8e76-d92e4bc92f01/download/bgd_admbnda_adm1_bbs_20201113.geojson',
]

data = None
for url in urls:
    try:
        print('Trying:', url[:80])
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode('utf-8')
            data = json.loads(raw)
            ftype = data.get('type','')
            feats = data.get('features', [])
            print('SUCCESS! type=%s features=%d' % (ftype, len(feats)))
            for f in feats[:3]:
                print('  Props:', json.dumps(f.get('properties',{}))[:200])
            break
    except Exception as e:
        print('Failed:', str(e)[:100])

if data:
    with open(r'e:\ITL FINAL ADV ANALYSIS\bd_raw.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print('Saved bd_raw.json')
else:
    print('ALL FAILED')
    sys.exit(1)
