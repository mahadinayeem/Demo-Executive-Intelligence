
import re

html_path = 'ceo_national_map.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace isOutletMatch
old_match = '''function isOutletMatch(o) {
  const [lat,lng,id,name,didx,dist,score,status,rev,visits,lastVisit,daysSince,srName,orders,avgRPV] = o;
  if (healthFilter !== 'ALL' && status !== healthFilter) return false;
  if (subTierFilter !== 'ALL') {
    const st = classifySubTier(status, score, rev, visits, orders, daysSince, avgRPV);
    if (st.tier !== subTierFilter) return false;
  }
  return true;
}'''

new_match = '''function isOutletMatch(o) {
  const [lat,lng,id,name,didx,dist,score,status,rev,visits,lastVisit,daysSince,srName,orders,avgRPV] = o;
  
  if (healthFilter === 'ZV') {
    if ((visits || 0) > 0) return false;
    if (subTierFilter === 'ZV_UNASSIGNED' && (srName && srName !== 'N/A')) return false;
    if (subTierFilter === 'ZV_DORMANT' && (daysSince < 90 && daysSince !== 999)) return false;
    return true;
  }
  
  if (healthFilter === 'ZR') {
    if ((rev || 0) > 0) return false;
    if (subTierFilter === 'ZR_VISITED_NO_ORDER' && (visits || 0) === 0) return false;
    if (subTierFilter === 'ZR_UNVISITED' && (visits || 0) > 0) return false;
    return true;
  }

  if (healthFilter !== 'ALL' && status !== healthFilter) return false;
  if (subTierFilter !== 'ALL') {
    const st = classifySubTier(status, score, rev, visits, orders, daysSince, avgRPV);
    if (st.tier !== subTierFilter) return false;
  }
  return true;
}'''

html = html.replace(old_match, new_match)

# Replace updateKPIs
old_kpi = '''function updateKPIs() {
  try {
    let tot=0, str=0, mod=0, wk=0, rev=0, vis=0;
    
    if (!activeDivision) {
      CEO_NATIONAL.divisions.forEach(x => {
        tot += x.outlets; str += x.strong||0; mod += x.moderate||0; wk += x.weak||0;
        rev += x.revenue||0; vis += x.visits||0;
      });
    } else if (activeDivision && !activeDistrict) {
      const d = CEO_NATIONAL.divisions.find(x => x.name === activeDivision) || {};
      tot = d.outlets||0; str = d.strong||0; mod = d.moderate||0; wk = d.weak||0;
      rev = d.revenue||0; vis = d.visits||0;
    } else {
      const divIdx = DIV_NAMES.indexOf(activeDivision);
      const allOutlets = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
      const distOutlets = allOutlets.filter(o => o[5] && o[5].toLowerCase() === activeDistrict.toLowerCase() && (!activeThana || (o[16] && o[16].toLowerCase() === activeThana.toLowerCase())));
      
      tot = distOutlets.length;
      distOutlets.forEach(o => {
        if (o[7] === 'G') str++;
        else if (o[7] === 'Y') mod++;
        else if (o[7] === 'R') wk++;
        rev += (o[8]||0);
        vis += (o[9]||0);
      });
    }

    let displayCount = tot;
    if (healthFilter === 'G') displayCount = str;
    else if (healthFilter === 'Y') displayCount = mod;
    else if (healthFilter === 'R') displayCount = wk;

    document.getElementById('kTotal').textContent  = displayCount.toLocaleString();
    document.getElementById('kStrong').textContent = str.toLocaleString();
    document.getElementById('kMod').textContent    = mod.toLocaleString();
    document.getElementById('kWeak').textContent   = wk.toLocaleString();
    document.getElementById('kRev').textContent    = rev > 1e9 ? '৳'+(rev/1e9).toFixed(1)+'B' : '৳'+(rev/1e6).toFixed(1)+'M';
    document.getElementById('kVis').textContent    = (vis/1e6).toFixed(2)+'M';
  } catch(e){}
}'''

new_kpi = '''function updateKPIs() {
  try {
    let tot=0, str=0, mod=0, wk=0, rev=0, vis=0, zv=0, zr=0;
    
    if (!activeDivision) {
      CEO_NATIONAL.divisions.forEach(x => {
        tot += x.outlets; str += x.strong||0; mod += x.moderate||0; wk += x.weak||0;
        rev += x.revenue||0; vis += x.visits||0;
        zv += x.zero_visits||0; zr += x.zero_rev||0;
      });
    } else if (activeDivision && !activeDistrict) {
      const d = CEO_NATIONAL.divisions.find(x => x.name === activeDivision) || {};
      tot = d.outlets||0; str = d.strong||0; mod = d.moderate||0; wk = d.weak||0;
      rev = d.revenue||0; vis = d.visits||0;
      zv = d.zero_visits||0; zr = d.zero_rev||0;
    } else {
      const divIdx = DIV_NAMES.indexOf(activeDivision);
      const allOutlets = (typeof CEO_OUTLETS !== 'undefined' ? CEO_OUTLETS[divIdx] : null) || [];
      const distOutlets = allOutlets.filter(o => o[5] && o[5].toLowerCase() === activeDistrict.toLowerCase() && (!activeThana || (o[16] && o[16].toLowerCase() === activeThana.toLowerCase())));
      
      tot = distOutlets.length;
      distOutlets.forEach(o => {
        if (o[7] === 'G') str++;
        else if (o[7] === 'Y') mod++;
        else if (o[7] === 'R') wk++;
        if ((o[9]||0) === 0) zv++;
        if ((o[8]||0) === 0) zr++;
        rev += (o[8]||0);
        vis += (o[9]||0);
      });
    }

    let displayCount = tot;
    if (healthFilter === 'G') displayCount = str;
    else if (healthFilter === 'Y') displayCount = mod;
    else if (healthFilter === 'R') displayCount = wk;
    else if (healthFilter === 'ZV') displayCount = zv;
    else if (healthFilter === 'ZR') displayCount = zr;

    document.getElementById('kTotal').textContent   = displayCount.toLocaleString();
    document.getElementById('kStrong').textContent  = str.toLocaleString();
    document.getElementById('kMod').textContent     = mod.toLocaleString();
    document.getElementById('kWeak').textContent    = wk.toLocaleString();
    if(document.getElementById('kZeroVis')) document.getElementById('kZeroVis').textContent = zv.toLocaleString() + ' (' + (tot?Math.round((zv/tot)*100):0) + '%)';
    if(document.getElementById('kZeroRev')) document.getElementById('kZeroRev').textContent = zr.toLocaleString() + ' (' + (tot?Math.round((zr/tot)*100):0) + '%)';
    if(document.getElementById('sbZVCount')) document.getElementById('sbZVCount').textContent = '(' + (zv >= 1000 ? (zv/1000).toFixed(1)+'k' : zv) + ')';
    if(document.getElementById('sbZRCount')) document.getElementById('sbZRCount').textContent = '(' + (zr >= 1000 ? (zr/1000).toFixed(1)+'k' : zr) + ')';
    document.getElementById('kRev').textContent     = rev > 1e9 ? '৳'+(rev/1e9).toFixed(1)+'B' : '৳'+(rev/1e6).toFixed(1)+'M';
    document.getElementById('kVis').textContent     = (vis/1e6).toFixed(2)+'M';
  } catch(e){}
}'''

html = html.replace(old_kpi, new_kpi)

# Replace cluster creation icon logic
old_cluster_func = '''    iconCreateFunction: function(cluster) {
      const markers = cluster.getAllChildMarkers();
      const count = markers.length;
      
      let cls = 'cluster-mix';
      if (healthFilter === 'G') cls = 'cluster-g';
      else if (healthFilter === 'Y') cls = 'cluster-y';
      else if (healthFilter === 'R') cls = 'cluster-r';
      else {
        const gCnt = markers.filter(m => m.options.outletStatus === 'G').length;
        const rCnt = markers.filter(m => m.options.outletStatus === 'R').length;
        if (gCnt === count) cls = 'cluster-g';
        else if (rCnt === count) cls = 'cluster-r';
        else if (gCnt > rCnt) cls = 'cluster-g';
        else if (rCnt > gCnt) cls = 'cluster-r';
        else cls = 'cluster-y';
      }'''

new_cluster_func = '''    iconCreateFunction: function(cluster) {
      const markers = cluster.getAllChildMarkers();
      const count = markers.length;
      
      let cls = 'cluster-mix';
      if (healthFilter === 'G') cls = 'cluster-g';
      else if (healthFilter === 'Y') cls = 'cluster-y';
      else if (healthFilter === 'R') cls = 'cluster-r';
      else if (healthFilter === 'ZV') cls = 'cluster-zv';
      else if (healthFilter === 'ZR') cls = 'cluster-zr';
      else {
        const gCnt = markers.filter(m => m.options.outletStatus === 'G').length;
        const rCnt = markers.filter(m => m.options.outletStatus === 'R').length;
        if (gCnt === count) cls = 'cluster-g';
        else if (rCnt === count) cls = 'cluster-r';
        else if (gCnt > rCnt) cls = 'cluster-g';
        else if (rCnt > gCnt) cls = 'cluster-r';
        else cls = 'cluster-y';
      }'''

html = html.replace(old_cluster_func, new_cluster_func)

# Replace division polygon draw count logic
old_div_poly = '''    let count = divDat.outlets || 0;
    if (healthFilter === 'G') count = divDat.strong || 0;
    else if (healthFilter === 'Y') count = divDat.moderate || 0;
    else if (healthFilter === 'R') count = divDat.weak || 0;'''

new_div_poly = '''    let count = divDat.outlets || 0;
    if (healthFilter === 'G') count = divDat.strong || 0;
    else if (healthFilter === 'Y') count = divDat.moderate || 0;
    else if (healthFilter === 'R') count = divDat.weak || 0;
    else if (healthFilter === 'ZV') count = divDat.zero_visits || 0;
    else if (healthFilter === 'ZR') count = divDat.zero_rev || 0;'''

html = html.replace(old_div_poly, new_div_poly)

# Replace district polygon draw count logic
old_dist_poly = '''    let count = distDat.outlets || 0;
    if (healthFilter === 'G') count = distDat.strong || 0;
    else if (healthFilter === 'Y') count = distDat.moderate || 0;
    else if (healthFilter === 'R') count = distDat.weak || 0;'''

new_dist_poly = '''    let count = distDat.outlets || 0;
    if (healthFilter === 'G') count = distDat.strong || 0;
    else if (healthFilter === 'Y') count = distDat.moderate || 0;
    else if (healthFilter === 'R') count = distDat.weak || 0;
    else if (healthFilter === 'ZV') count = distDat.zero_visits || 0;
    else if (healthFilter === 'ZR') count = distDat.zero_rev || 0;'''

html = html.replace(old_dist_poly, new_dist_poly)

# Replace division sidebar cards
old_div_side = '''    let count = d.outlets;
    if (healthFilter === 'G') count = d.strong||0;
    else if (healthFilter === 'Y') count = d.moderate||0;
    else if (healthFilter === 'R') count = d.weak||0;

    const pct = d.outlets ? Math.round(((d.strong||0)/d.outlets)*100) : 0;
    el.innerHTML = `<div class="dn">${d.name}</div><div class="dc">${count.toLocaleString()}</div><div class="dm">${pct}% Strong • ৳${((d.revenue||0)/1e9).toFixed(1)}B</div>`;'''

new_div_side = '''    let count = d.outlets;
    let subTxt = '';
    if (healthFilter === 'G') { count = d.strong||0; subTxt = Math.round((count/d.outlets)*100) + '% Strong'; }
    else if (healthFilter === 'Y') { count = d.moderate||0; subTxt = Math.round((count/d.outlets)*100) + '% Moderate'; }
    else if (healthFilter === 'R') { count = d.weak||0; subTxt = Math.round((count/d.outlets)*100) + '% Weak'; }
    else if (healthFilter === 'ZV') { count = d.zero_visits||0; subTxt = Math.round((count/d.outlets)*100) + '% 0-Visits (Blind Spot)'; }
    else if (healthFilter === 'ZR') { count = d.zero_rev||0; subTxt = Math.round((count/d.outlets)*100) + '% 0-Revenue (Dead Zone)'; }
    else { const pct = d.outlets ? Math.round(((d.strong||0)/d.outlets)*100) : 0; subTxt = `${pct}% Strong • ৳${((d.revenue||0)/1e9).toFixed(1)}B`; }

    el.innerHTML = `<div class="dn">${d.name}</div><div class="dc">${count.toLocaleString()}</div><div class="dm">${subTxt}</div>`;'''

html = html.replace(old_div_side, new_div_side)

# Replace dist panel sort and count
old_dist_panel = '''  dists.sort((a,b)=> {
    let ca = healthFilter==='G'?a.strong:healthFilter==='Y'?a.moderate:healthFilter==='R'?a.weak:a.outlets;
    let cb = healthFilter==='G'?b.strong:healthFilter==='Y'?b.moderate:healthFilter==='R'?b.weak:b.outlets;
    return cb - ca;
  }).forEach(d=>{
    let count = d.outlets;
    if (healthFilter === 'G') count = d.strong||0;
    else if (healthFilter === 'Y') count = d.moderate||0;
    else if (healthFilter === 'R') count = d.weak||0;'''

new_dist_panel = '''  dists.sort((a,b)=> {
    let ca = healthFilter==='G'?a.strong:healthFilter==='Y'?a.moderate:healthFilter==='R'?a.weak:healthFilter==='ZV'?a.zero_visits:healthFilter==='ZR'?a.zero_rev:a.outlets;
    let cb = healthFilter==='G'?b.strong:healthFilter==='Y'?b.moderate:healthFilter==='R'?b.weak:healthFilter==='ZV'?b.zero_visits:healthFilter==='ZR'?b.zero_rev:b.outlets;
    return cb - ca;
  }).forEach(d=>{
    let count = d.outlets;
    if (healthFilter === 'G') count = d.strong||0;
    else if (healthFilter === 'Y') count = d.moderate||0;
    else if (healthFilter === 'R') count = d.weak||0;
    else if (healthFilter === 'ZV') count = d.zero_visits||0;
    else if (healthFilter === 'ZR') count = d.zero_rev||0;'''

html = html.replace(old_dist_panel, new_dist_panel)

# Replace thana panel map builder
old_thana_map = '''  distOutlets.forEach(o => {
    const t = o[16] || 'Other';
    if (!thanaMap[t]) thanaMap[t] = { name: t, outlets: 0, strong: 0, moderate: 0, weak: 0 };
    thanaMap[t].outlets++;
    if (o[7] === 'G') thanaMap[t].strong++;
    else if (o[7] === 'Y') thanaMap[t].moderate++;
    else if (o[7] === 'R') thanaMap[t].weak++;
  });'''

new_thana_map = '''  distOutlets.forEach(o => {
    const t = o[16] || 'Other';
    if (!thanaMap[t]) thanaMap[t] = { name: t, outlets: 0, strong: 0, moderate: 0, weak: 0, zero_visits: 0, zero_rev: 0 };
    thanaMap[t].outlets++;
    if (o[7] === 'G') thanaMap[t].strong++;
    else if (o[7] === 'Y') thanaMap[t].moderate++;
    else if (o[7] === 'R') thanaMap[t].weak++;
    if ((o[9]||0) === 0) thanaMap[t].zero_visits++;
    if ((o[8]||0) === 0) thanaMap[t].zero_rev++;
  });'''

html = html.replace(old_thana_map, new_thana_map)

# Replace thana panel sort and count
old_thana_panel = '''  thanaList.sort((a,b)=> {
    let ca = healthFilter==='G'?a.strong:healthFilter==='Y'?a.moderate:healthFilter==='R'?a.weak:a.outlets;
    let cb = healthFilter==='G'?b.strong:healthFilter==='Y'?b.moderate:healthFilter==='R'?b.weak:b.outlets;
    return cb - ca;
  }).forEach(t=>{
    let count = t.outlets;
    if (healthFilter === 'G') count = t.strong||0;
    else if (healthFilter === 'Y') count = t.moderate||0;
    else if (healthFilter === 'R') count = t.weak||0;'''

new_thana_panel = '''  thanaList.sort((a,b)=> {
    let ca = healthFilter==='G'?a.strong:healthFilter==='Y'?a.moderate:healthFilter==='R'?a.weak:healthFilter==='ZV'?a.zero_visits:healthFilter==='ZR'?a.zero_rev:a.outlets;
    let cb = healthFilter==='G'?b.strong:healthFilter==='Y'?b.moderate:healthFilter==='R'?b.weak:healthFilter==='ZV'?b.zero_visits:healthFilter==='ZR'?b.zero_rev:b.outlets;
    return cb - ca;
  }).forEach(t=>{
    let count = t.outlets;
    if (healthFilter === 'G') count = t.strong||0;
    else if (healthFilter === 'Y') count = t.moderate||0;
    else if (healthFilter === 'R') count = t.weak||0;
    else if (healthFilter === 'ZV') count = t.zero_visits||0;
    else if (healthFilter === 'ZR') count = t.zero_rev||0;'''

html = html.replace(old_thana_panel, new_thana_panel)

# Replace sub tier controls builder
old_subtier_func = '''function buildSubTierControls(f) {
  const box = document.getElementById('subtierBox');
  const title = document.getElementById('subtierTitle');
  const btns = document.getElementById('subtierBtns');

  if (f === 'ALL') {
    box.style.display = 'none';
    subTierFilter = 'ALL';
    return;
  }

  box.style.display = 'flex';
  btns.innerHTML = '';

  let tiers = [];
  if (f === 'G') {
    title.textContent = '🟢 Strong Sub-Tiers';
    tiers = [
      {id:'ALL', name:'All Strong', cls:'g-act'},
      {id:'G1', name:'Platinum (Tier 1)', cls:'g-act'},
      {id:'G2', name:'Gold (Tier 2)', cls:'g-act'},
      {id:'G3', name:'Silver (Tier 3)', cls:'g-act'}
    ];
  } else if (f === 'Y') {
    title.textContent = '🟡 Moderate Sub-Tiers';
    tiers = [
      {id:'ALL', name:'All Moderate', cls:'y-act'},
      {id:'Y1', name:'High Mod (Growth)', cls:'y-act'},
      {id:'Y2', name:'Core Mod (Steady)', cls:'y-act'},
      {id:'Y3', name:'Slipping (At-Risk)', cls:'y-act'}
    ];
  } else if (f === 'R') {
    title.textContent = '🔴 Weak Sub-Tiers';
    tiers = [
      {id:'ALL', name:'All Weak', cls:'r-act'},
      {id:'R1', name:'Critical (0 Visit)', cls:'r-act'},
      {id:'R2', name:'High Visit 0 Order', cls:'r-act'},
      {id:'R3', name:'Low / Dropping', cls:'r-act'}
    ];
  }

  tiers.forEach(t => {
    const btn = document.createElement('div');
    btn.className = 'st-btn' + (subTierFilter === t.id ? ' ' + t.cls : '');
    btn.textContent = t.name;
    btn.onclick = () => {
      subTierFilter = t.id;
      document.querySelectorAll('.st-btn').forEach(b => b.className = 'st-btn');
      btn.className = 'st-btn ' + t.cls;
      if(activeDistrict && activeDivision){
        renderMicroOutlets(DIV_NAMES.indexOf(activeDivision), activeDistrict);
      }
    };
    btns.appendChild(btn);
  });
}'''

new_subtier_func = '''function buildSubTierControls(f) {
  const box = document.getElementById('subtierBox');
  const title = document.getElementById('subtierTitle');
  const btns = document.getElementById('subtierBtns');

  if (f === 'ALL') {
    box.style.display = 'none';
    subTierFilter = 'ALL';
    return;
  }

  box.style.display = 'flex';
  btns.innerHTML = '';

  let tiers = [];
  if (f === 'G') {
    title.textContent = '🟢 Strong Sub-Tiers';
    tiers = [
      {id:'ALL', name:'All Strong', cls:'g-act'},
      {id:'G1', name:'Platinum (Tier 1)', cls:'g-act'},
      {id:'G2', name:'Gold (Tier 2)', cls:'g-act'},
      {id:'G3', name:'Silver (Tier 3)', cls:'g-act'}
    ];
  } else if (f === 'Y') {
    title.textContent = '🟡 Moderate Sub-Tiers';
    tiers = [
      {id:'ALL', name:'All Moderate', cls:'y-act'},
      {id:'Y1', name:'High Mod (Growth)', cls:'y-act'},
      {id:'Y2', name:'Core Mod (Steady)', cls:'y-act'},
      {id:'Y3', name:'Slipping (At-Risk)', cls:'y-act'}
    ];
  } else if (f === 'R') {
    title.textContent = '🔴 Weak Sub-Tiers';
    tiers = [
      {id:'ALL', name:'All Weak', cls:'r-act'},
      {id:'R1', name:'Critical (0 Visit)', cls:'r-act'},
      {id:'R2', name:'High Visit 0 Order', cls:'r-act'},
      {id:'R3', name:'Low / Dropping', cls:'r-act'}
    ];
  } else if (f === 'ZV') {
    title.textContent = '🚫 0-Visit Diagnostic Breakdown';
    tiers = [
      {id:'ALL', name:'All 0-Visits (72.6k)', cls:'zv-act'},
      {id:'ZV_UNASSIGNED', name:'Unassigned SR', cls:'zv-act'},
      {id:'ZV_DORMANT', name:'Dormant >90 Days', cls:'zv-act'}
    ];
  } else if (f === 'ZR') {
    title.textContent = '💸 0-Revenue Diagnostic Breakdown';
    tiers = [
      {id:'ALL', name:'All 0-Revenue (72.5k)', cls:'zr-act'},
      {id:'ZR_VISITED_NO_ORDER', name:'Visited But 0 Orders', cls:'zr-act'},
      {id:'ZR_UNVISITED', name:'0-Visit & 0-Revenue', cls:'zr-act'}
    ];
  }

  tiers.forEach(t => {
    const btn = document.createElement('div');
    btn.className = 'st-btn' + (subTierFilter === t.id ? ' ' + t.cls : '');
    btn.textContent = t.name;
    btn.onclick = () => {
      subTierFilter = t.id;
      document.querySelectorAll('.st-btn').forEach(b => b.className = 'st-btn');
      btn.className = 'st-btn ' + t.cls;
      if(activeDistrict && activeDivision){
        renderMicroOutlets(DIV_NAMES.indexOf(activeDivision), activeDistrict, activeThana);
      }
    };
    btns.appendChild(btn);
  });
}'''

html = html.replace(old_subtier_func, new_subtier_func)

# Replace setF function
old_setF = '''function setF(f){
  healthFilter=f;
  subTierFilter='ALL';
  ['fbA','fbG','fbY','fbR'].forEach(id=>{ document.getElementById(id).className='fb'; });
  const m={ALL:['fbA','fa'],G:['fbG','fg'],Y:['fbY','fy'],R:['fbR','fr']};
  document.getElementById(m[f][0]).classList.add(m[f][1]);

  buildSubTierControls(f);
  updateKPIs();
  buildDivSidebar();

  if(!activeDivision){
    drawDivisionPolygons();
  } else if(activeDivision && !activeDistrict){
    buildDistPanel(activeDivision, DIV_NAMES.indexOf(activeDivision));
    drawDistrictPolygons(activeDivision, DIV_NAMES.indexOf(activeDivision));
  } else if(activeDistrict && activeDivision){
    buildThanaPanel(activeDistrict, DIV_NAMES.indexOf(activeDivision));
    if (!activeThana) {
      drawThanaPolygons(activeDistrict, DIV_NAMES.indexOf(activeDivision));
    }
    renderMicroOutlets(DIV_NAMES.indexOf(activeDivision), activeDistrict, activeThana);
  }
}'''

new_setF = '''function setF(f){
  healthFilter=f;
  subTierFilter='ALL';
  ['fbA','fbG','fbY','fbR','fbZV','fbZR'].forEach(id=>{ 
    const el = document.getElementById(id);
    if(el) el.className='fb'; 
  });
  const m={
    ALL:['fbA','fa'],
    G:['fbG','fg'],
    Y:['fbY','fy'],
    R:['fbR','fr'],
    ZV:['fbZV','fzv'],
    ZR:['fbZR','fzr']
  };
  if (m[f] && document.getElementById(m[f][0])) {
    document.getElementById(m[f][0]).classList.add(m[f][1]);
  }

  buildSubTierControls(f);
  updateKPIs();
  buildDivSidebar();

  if(!activeDivision){
    drawDivisionPolygons();
  } else if(activeDivision && !activeDistrict){
    buildDistPanel(activeDivision, DIV_NAMES.indexOf(activeDivision));
    drawDistrictPolygons(activeDivision, DIV_NAMES.indexOf(activeDivision));
  } else if(activeDistrict && activeDivision){
    buildThanaPanel(activeDistrict, DIV_NAMES.indexOf(activeDivision));
    if (!activeThana) {
      drawThanaPolygons(activeDistrict, DIV_NAMES.indexOf(activeDivision));
    }
    renderMicroOutlets(DIV_NAMES.indexOf(activeDivision), activeDistrict, activeThana);
  }
}'''

html = html.replace(old_setF, new_setF)

# Replace circleMarker color logic in renderMicroOutlets
old_pin_style = '''      mk = L.circleMarker([lat,lng],{
        radius: 9,
        fillColor: st.color,
        color: '#ffffff',
        weight: 2.5,
        opacity: 1.0,
        fillOpacity: 0.95,
        outletStatus: status,
        interactive: true
      });'''

new_pin_style = '''      let pinColor = st.color;
      if (healthFilter === 'ZV') pinColor = '#a855f7';
      else if (healthFilter === 'ZR') pinColor = '#f43f5e';

      mk = L.circleMarker([lat,lng],{
        radius: 9,
        fillColor: pinColor,
        color: '#ffffff',
        weight: 2.5,
        opacity: 1.0,
        fillOpacity: 0.95,
        outletStatus: status,
        interactive: true
      });'''

html = html.replace(old_pin_style, new_pin_style)

# Replace downloadFilteredCSV
old_csv = '''      const st = classifySubTier(status, score, rev, visits, orders, daysSince, avgRPV);
      exportData.push({
        'Outlet_ID': id,
        'Outlet_Name': name,
        'Division': DIV_NAMES[didx],
        'District': dist,
        'Thana_Upazila': thana || 'N/A',
        'Primary_Health': status === 'G' ? 'Strong' : status === 'Y' ? 'Moderate' : 'Weak',
        'Sub_Tier': st.name,
        'Health_Score': score,
        'Diagnosis_Why_Reason': st.desc.replace(/,/g, ';'),
        '4M_Revenue_BDT': rev,
        'Orders_Count': orders,
        'Visits_Count': visits,
        'Last_Visit_Date': lastVisit || 'None',
        'Days_Since_Last_Visit': daysSince,
        'Assigned_SR': srName,
        'Revenue_Per_Visit': avgRPV,
        'Month_Minus_3_Revenue': trend && trend[0] ? trend[0] : 0,
        'Month_Minus_2_Revenue': trend && trend[1] ? trend[1] : 0,
        'Month_Minus_1_Revenue': trend && trend[2] ? trend[2] : 0,
        'Current_Month_Revenue': trend && trend[3] ? trend[3] : 0,
        'Latitude': lat,
        'Longitude': lng
      });'''

new_csv = '''      const st = classifySubTier(status, score, rev, visits, orders, daysSince, avgRPV);
      let gapType = 'Active Performer';
      if ((visits||0) === 0) gapType = '0-Visit Blind Spot (No SR Visits in 4M)';
      else if ((rev||0) === 0) gapType = '0-Revenue Conversion Barrier (Visited But 0 Sales)';
      else if (status === 'R') gapType = 'At-Risk Weak Buyer';

      exportData.push({
        'Outlet_ID': id,
        'Outlet_Name': name,
        'Division': DIV_NAMES[didx],
        'District': dist,
        'Thana_Upazila': thana || 'N/A',
        'Primary_Health': status === 'G' ? 'Strong' : status === 'Y' ? 'Moderate' : 'Weak',
        'Sub_Tier': st.name,
        'Is_Zero_Visits_4M': (visits||0) === 0 ? 'YES' : 'NO',
        'Is_Zero_Revenue_4M': (rev||0) === 0 ? 'YES' : 'NO',
        'Field_Gap_Diagnosis': gapType,
        'Health_Score': score,
        'Diagnosis_Why_Reason': st.desc.replace(/,/g, ';'),
        '4M_Revenue_BDT': rev,
        'Orders_Count': orders,
        'Visits_Count': visits,
        'Last_Visit_Date': lastVisit || 'None',
        'Days_Since_Last_Visit': daysSince,
        'Assigned_SR': srName,
        'Revenue_Per_Visit': avgRPV,
        'Month_Minus_3_Revenue': trend && trend[0] ? trend[0] : 0,
        'Month_Minus_2_Revenue': trend && trend[1] ? trend[1] : 0,
        'Month_Minus_1_Revenue': trend && trend[2] ? trend[2] : 0,
        'Current_Month_Revenue': trend && trend[3] ? trend[3] : 0,
        'Latitude': lat,
        'Longitude': lng
      });'''

html = html.replace(old_csv, new_csv)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("JS logic updated successfully!")
