"""
Enhance Thana panel with visual Untapped indicators
"""

path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_thana_row = '''    const row = document.createElement('div');
    row.className = 'drow' + (activeThana === t.name ? ' sel' : '');
    row.id = 'tr_'+t.name.replace(/\s+/g,'_');
    row.onclick = () => {
      drillThana(t.name, distName, divIdx);
    };
    row.innerHTML = `<span class="drn">${t.name}</span><span class="drc">${count.toLocaleString()}</span>`;
    scroll.appendChild(row);'''

new_thana_row = '''    const isThanaUntapped = (t.zero_visits === t.outlets || (t.strong === 0 && t.moderate === 0));
    const row = document.createElement('div');
    row.className = 'drow' + (activeThana === t.name ? ' sel' : '') + (isThanaUntapped ? ' unt-thana-row' : '');
    row.id = 'tr_'+t.name.replace(/\s+/g,'_');
    row.onclick = () => {
      drillThana(t.name, distName, divIdx);
    };
    const tagHtml = isThanaUntapped 
      ? `<span style="background:rgba(239,68,68,0.15);color:#ef4444;padding:1px 5px;border-radius:4px;font-size:8.5px;font-weight:900;">⚠️ Untapped</span>` 
      : '';
    row.innerHTML = `<span class="drn" style="display:flex;align-items:center;gap:5px;"><span>${t.name}</span>${tagHtml}</span><span class="drc">${count.toLocaleString()}</span>`;
    scroll.appendChild(row);'''

content = content.replace(old_thana_row, new_thana_row)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Enhanced buildThanaPanel successfully!")
