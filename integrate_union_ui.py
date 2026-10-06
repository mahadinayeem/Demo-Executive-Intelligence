"""
Integrate Union-level Drill-down Panel, Tooltips, and Strict BBS Filtering into ceo_national_map.html
"""
import re

path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Union Panel HTML in Sidebar (right after thanaPanel)
union_panel_html = '''
    <div class="sb dp" id="unionPanel">
      <div class="sb-hd">
        <span class="sb-ttl" id="unionTitle">Unions &amp; Wards</span>
        <span style="font-size:9.5px;color:var(--t3);" id="unionBadge"></span>
      </div>
      <div class="dscrl" id="unionScroll"></div>
    </div>'''

if 'id="unionPanel"' not in content:
    content = content.replace('    <div class="sb dp" id="thanaPanel">', union_panel_html + '\n    <div class="sb dp" id="thanaPanel">')

# 2. Add activeUnion state variable
if 'let activeUnion = null;' not in content:
    content = content.replace('let activeThana = null;', 'let activeThana = null, activeUnion = null;')

# 3. Update renderMicroOutlets to include Union filtering and display
old_micro_render = '''    const isOrdered = ((rev||0) > 0 || (orders||0) > 0);
    const isVisitedNoOrder = ((visits||0) > 0 && !isOrdered);
    const isUntapped = ((visits||0) === 0);

    if (isOrdered) {
      tierName = 'Ordered Outlet';
      dotColor = '#10b981'; // Emerald Green
    } else if (isVisitedNoOrder) {
      tierName = 'Visited (No Order)';
      dotColor = '#f59e0b'; // Amber Gold
    } else {
      tierName = 'Untapped Outlet (0 Visits)';
      dotColor = '#ef4444'; // Vibrant Coral Red
    }'''

new_micro_render = '''    const unionName = o[17] || 'Ward/Union Area';
    
    // Optional Union filter
    if (activeUnion && unionName.toLowerCase() !== activeUnion.toLowerCase()) return;

    const isOrdered = ((rev||0) > 0 || (orders||0) > 0);
    const isVisitedNoOrder = ((visits||0) > 0 && !isOrdered);
    const isUntapped = ((visits||0) === 0);

    if (isOrdered) {
      tierName = 'Ordered Outlet';
      dotColor = '#10b981'; // Emerald Green
    } else if (isVisitedNoOrder) {
      tierName = 'Visited (No Order)';
      dotColor = '#f59e0b'; // Amber Gold
    } else {
      tierName = 'Untapped Outlet (0 Visits)';
      dotColor = '#ef4444'; // Vibrant Coral Red
    }'''

content = content.replace(old_micro_render, new_micro_render)

# 4. Update Tooltip to show Union
old_tooltip = '''    // Rich Tooltip on hover
    mk.bindTooltip(`
      <div style="font-family:'Outfit',sans-serif;font-size:12px;font-weight:700;line-height:1.4;">
        <div style="display:flex;align-items:center;gap:5px;margin-bottom:2px;">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${dotColor};border:1px solid #fff;"></span>
          <span style="color:${dotColor};font-weight:900;">${tierName}</span>
        </div>
        <b>${name}</b> <span style="font-size:10px;opacity:0.8;">(#${id})</span><br>
        <div style="font-size:11px;color:#cbd5e1;margin-top:2px;">
          💰 Sales: <b>৳${(rev||0).toLocaleString()}</b> | 🛒 Orders: <b>${orders||0}</b><br>
          🚗 Visits: <b>${visits||0}</b> | 👤 SR: <b>${srName||'Unassigned'}</b>
        </div>
      </div>`, {direction:'top', offset:[0,-6], className:'div-tooltip'});'''

new_tooltip = '''    // Rich Tooltip on hover with Union & Thana
    const uNameDisplay = o[17] || 'Ward Area';
    mk.bindTooltip(`
      <div style="font-family:'Outfit',sans-serif;font-size:12px;font-weight:700;line-height:1.4;min-width:180px;">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:5px;margin-bottom:2px;">
          <span style="display:flex;align-items:center;gap:4px;">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${dotColor};border:1px solid #fff;"></span>
            <span style="color:${dotColor};font-weight:900;">${tierName}</span>
          </span>
          <span style="font-size:9.5px;color:#93c5fd;font-weight:800;">📍 ${uNameDisplay}</span>
        </div>
        <b>${name}</b> <span style="font-size:10px;opacity:0.8;">(#${id})</span><br>
        <div style="font-size:10.5px;color:#e2e8f0;margin-top:3px;border-top:1px dashed rgba(255,255,255,0.2);padding-top:3px;">
          🏛️ <b>${dist}, ${o[16]||''}</b> (Union: <b>${uNameDisplay}</b>)<br>
          💰 Sales: <b>৳${(rev||0).toLocaleString()}</b> | 🛒 Orders: <b>${orders||0}</b><br>
          🚗 Visits: <b>${visits||0}</b> | 👤 SR: <b>${srName||'Unassigned'}</b>
        </div>
      </div>`, {direction:'top', offset:[0,-6], className:'div-tooltip'});'''

content = content.replace(old_tooltip, new_tooltip)

# 5. Add buildUnionPanel and drillUnion functions
union_js = '''
/* ═══════════════ UNION LEVEL DRILL-DOWN & HIERARCHY ═══════════════ */
function buildUnionPanel(thanaName, distName, divIdx) {
  const panel = document.getElementById('unionPanel');
  const scroll = document.getElementById('unionScroll');
  if (!panel || !scroll) return;

  document.getElementById('unionTitle').textContent = thanaName + ' Unions';
  panel.style.display = 'block';

  const allOutlets = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
  const thanaOutlets = allOutlets.filter(o => 
    o[5] && o[5].toLowerCase() === distName.toLowerCase() &&
    o[16] && o[16].toLowerCase() === thanaName.toLowerCase()
  );

  const unionMap = {};
  thanaOutlets.forEach(o => {
    const u = o[17] || 'General Union';
    if (!unionMap[u]) unionMap[u] = { name: u, outlets: 0, ordered: 0, visitedNoOrder: 0, untapped: 0, rev: 0, visits: 0 };
    unionMap[u].outlets++;
    unionMap[u].rev += (o[8] || 0);
    unionMap[u].visits += (o[9] || 0);

    const isOrd = ((o[8]||0) > 0 || (o[13]||0) > 0);
    if (isOrd) unionMap[u].ordered++;
    else if ((o[9]||0) > 0) unionMap[u].visitedNoOrder++;
    else unionMap[u].untapped++;
  });

  const unionList = Object.values(unionMap);
  document.getElementById('unionBadge').textContent = unionList.length + ' Unions';
  scroll.innerHTML = '';

  // "All Unions" option
  const allRow = document.createElement('div');
  allRow.className = 'drow' + (!activeUnion ? ' sel' : '');
  allRow.onclick = () => {
    activeUnion = null;
    document.querySelectorAll('#unionScroll .drow').forEach(r => r.classList.remove('sel'));
    allRow.classList.add('sel');
    updateBC();
    updateKPIs();
    updateAdminSummaryPanel();
    renderMicroOutlets(divIdx, distName, thanaName);
  };
  allRow.innerHTML = `<span class="drn">🌐 All Unions</span><span class="drc">${thanaOutlets.length.toLocaleString()}</span>`;
  scroll.appendChild(allRow);

  unionList.sort((a,b) => b.outlets - a.outlets).forEach(u => {
    const row = document.createElement('div');
    row.className = 'drow' + (activeUnion === u.name ? ' sel' : '');
    row.onclick = () => {
      drillUnion(u.name, thanaName, distName, divIdx);
    };

    const isUnt = (u.visits === 0 && u.rev === 0);
    const untTag = isUnt ? `<span style="background:rgba(239,68,68,0.15);color:#ef4444;font-size:8px;padding:1px 4px;border-radius:3px;font-weight:900;">⚠️ Untapped</span>` : '';
    row.innerHTML = `<span class="drn" style="display:flex;align-items:center;gap:4px;"><span>${u.name}</span>${untTag}</span><span class="drc">${u.outlets.toLocaleString()}</span>`;
    scroll.appendChild(row);
  });
}

function drillUnion(unionName, thanaName, distName, divIdx) {
  activeUnion = unionName;
  document.querySelectorAll('#unionScroll .drow').forEach(r => {
    if (r.querySelector('.drn')?.textContent?.includes(unionName)) r.classList.add('sel');
    else r.classList.remove('sel');
  });

  updateBC();
  updateKPIs();
  updateAdminSummaryPanel();
  renderMicroOutlets(divIdx, distName, thanaName);
}
'''

content = content.replace('/* ═══════════════ DRILL THANA / UPAZILA ═══════════════ */',
                        union_js + '\n/* ═══════════════ DRILL THANA / UPAZILA ═══════════════ */')

# In drillThana, reset activeUnion and call buildUnionPanel
content = content.replace('activeThana = thanaName;', 'activeThana = thanaName;\n  activeUnion = null;\n  buildUnionPanel(thanaName, distName, divIdx);')

# In drillDistrict, hide unionPanel
content = content.replace('activeThana = null;', 'activeThana = null;\n  activeUnion = null;\n  const up = document.getElementById("unionPanel"); if(up) up.style.display="none";')

# In resetNational, hide unionPanel and thanaPanel
content = content.replace('function resetNational() {', 'function resetNational() {\n  activeDivision=null; activeDistrict=null; activeThana=null; activeUnion=null;\n  const up=document.getElementById("unionPanel"); if(up) up.style.display="none";\n  const tp=document.getElementById("thanaPanel"); if(tp) tp.style.display="none";\n  const dp=document.getElementById("distPanel"); if(dp) dp.style.display="none";')

# Update Breadcrumb to include Union
old_bc = '''  if(activeThana) bc.innerHTML += `<span class="bcs">›</span><span class="bcn here">${activeThana}</span>`;'''
new_bc = '''  if(activeThana) {
    if (activeUnion) {
      bc.innerHTML += `<span class="bcs">›</span><span class="bcn" onclick="drillThana('${activeThana}', '${activeDistrict}', ${activeDivision ? DIV_NAMES.indexOf(activeDivision) : 0})">${activeThana}</span>`;
      bc.innerHTML += `<span class="bcs">›</span><span class="bcn here">📍 ${activeUnion}</span>`;
    } else {
      bc.innerHTML += `<span class="bcs">›</span><span class="bcn here">${activeThana}</span>`;
    }
  }'''

content = content.replace(old_bc, new_bc)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully integrated Union-Level Drill-Down UI into ceo_national_map.html!")
