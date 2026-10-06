"""
Extract and check JS syntax of all scripts in ceo_national_map.html
"""
import re, subprocess

with open(r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    fname = f'scratch/test_script_{i}.js'
    with open(fname, 'w', encoding='utf-8') as sf:
        sf.write(s)
    
    res = subprocess.run(['node', '-c', fname], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR in script {i}:")
        print(res.stderr)
    else:
        print(f"Script {i} syntax is OK!")
