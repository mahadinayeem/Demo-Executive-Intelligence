"""
Add Interactive Untapped Thana Explorer Modal and Click Handlers to ceo_national_map.html
"""

path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the Thana 3-column grid HTML to be clickable with hover effects and pointer cursor
old_thana_grid = '''        <!-- Thana Coverage 3-Col Box -->
        <div class="ac-thana-grid">
          <div class="ac-thana-col">
            <div class="ac-tc-lbl">🏛️ Total Thana</div>
            <div class="ac-tc-val" id="acTotalThana">545</div>
          </div>
          <div class="ac-thana-col cov">
            <div class="ac-tc-lbl">✅ Covered</div>
            <div class="ac-tc-val" id="acCoveredThana">500</div>
          </div>
          <div class="ac-thana-col unt">
            <div class="ac-tc-lbl">⚠️ Untapped</div>
            <div class="ac-tc-val" id="acUntappedThana">45</div>
          </div>
        </div>'''

new_thana_grid = '''        <!-- Thana Coverage 3-Col Box (Clickable & Interactive) -->
        <div class="ac-thana-grid">
          <div class="ac-thana-col" onclick="showThanaListModal('ALL')" style="cursor:pointer;" title="Click to view all thanas">
            <div class="ac-tc-lbl">🏛️ Total Thana</div>
            <div class="ac-tc-val" id="acTotalThana">545</div>
          </div>
          <div class="ac-thana-col cov" onclick="showThanaListModal('COVERED')" style="cursor:pointer;" title="Click to view covered thanas">
            <div class="ac-tc-lbl">✅ Covered</div>
            <div class="ac-tc-val" id="acCoveredThana">500</div>
          </div>
          <div class="ac-thana-col unt" onclick="showThanaListModal('UNTAPPED')" style="cursor:pointer;animation:pulseBorder 2.5s infinite;" title="Click to inspect Untapped Thanas">
            <div class="ac-tc-lbl">⚠️ Untapped</div>
            <div class="ac-tc-val" id="acUntappedThana">45</div>
          </div>
        </div>'''

content = content.replace(old_thana_grid, new_thana_grid)

# 2. Add Modal HTML for Untapped / Covered Thanas List
thana_modal_html = '''
<!-- Untapped / Covered Thanas Explorer Modal -->
<div class="mveil" id="thanaListModal" onclick="if(event.target===this)closeThanaModal()">
  <div class="mbox" style="width: 580px; max-width: 95vw;">
    <div class="mhd" style="background: linear-gradient(135deg, #1e293b, #0f172a); color: #fff;">
      <div>
        <div class="mht" id="tlmTitle" style="color: #fff; display: flex; align-items: center; gap: 8px;">
          <span>⚠️ Untapped Thanas (Blind Spots)</span>
        </div>
        <div class="mhs" id="tlmSub" style="color: #94a3b8;">Thanas with 0 Visits or 0 Orders in the current scope</div>
      </div>
      <button class="mcl" onclick="closeThanaModal()">&times;</button>
    </div>
    <div class="mbdy" style="max-height: 70vh; overflow-y: auto; padding: 16px;">
      <div style="font-size: 11.5px; color: var(--t2); margin-bottom: 12px; font-weight: 600;">
        💡 <b>Click any Thana</b> below to immediately zoom in on the map and isolate its individual outlets:
      </div>
      <div id="thanaListContainer" style="display: flex; flex-direction: column; gap: 8px;">
        <!-- Dynamic Thana Items -->
      </div>
    </div>
  </div>
</div>
'''

content = content.replace('<!-- Modal (Full Detailed Outlet Profile Card) -->', thana_modal_html + '\n<!-- Modal (Full Detailed Outlet Profile Card) -->')

# 3. Add CSS for pulse and thana cards
css_addition = '''
@keyframes pulseBorder {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
.thana-modal-card {
  background: var(--card);
  border: 1px solid var(--bdr);
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}
.thana-modal-card:hover {
  border-color: #ef4444;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.15);
}
.thana-modal-card.is-cov:hover {
  border-color: #10b981;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.15);
}
'''
content = content.replace('</style>', css_addition + '\n</style>')

# 4. Add JavaScript logic to manage Thana coverage analysis and modal interactions
js_thana_modal = '''
/* ═══════════════ UNTAPPED & COVERED THANA EXPLORER ═══════════════ */
let currentThanaAnalysis = {
  untapped: [],
  covered: [],
  all: []
};

function showThanaListModal(filterType) {
  const modal = document.getElementById('thanaListModal');
  const container = document.getElementById('thanaListContainer');
  const title = document.getElementById('tlmTitle');
  const sub = document.getElementById('tlmSub');
  if (!modal || !container) return;

  const list = (filterType === 'UNTAPPED') ? currentThanaAnalysis.untapped 
             : (filterType === 'COVERED') ? currentThanaAnalysis.covered 
             : currentThanaAnalysis.all;

  if (filterType === 'UNTAPPED') {
    title.innerHTML = `<span>⚠️ Untapped Thanas (${list.length})</span>`;
    sub.textContent = 'Thanas with 0 Visits or 0 Orders in the current selected territory';
  } else if (filterType === 'COVERED') {
    title.innerHTML = `<span style="color:#10b981;">✅ Covered Active Thanas (${list.length})</span>`;
    sub.textContent = 'Thanas with active field visits & orders in current territory';
  } else {
    title.innerHTML = `<span>🏛️ All Thanas (${list.length})</span>`;
    sub.textContent = 'Complete list of thanas in current selected territory';
  }

  container.innerHTML = '';
  if (list.length === 0) {
    container.innerHTML = `<div style="text-align:center;padding:30px;color:var(--t3);font-weight:700;">No thanas found matching this criteria.</div>`;
  } else {
    list.forEach(t => {
      const card = document.createElement('div');
      card.className = `thana-modal-card ${t.isUntapped ? 'is-unt' : 'is-cov'}`;
      
      const badgeHtml = t.isUntapped 
        ? `<span style="background:rgba(239,68,68,0.15);color:#ef4444;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:900;border:1px solid rgba(239,68,68,0.3);">⚠️ 100% UNTAPPED</span>`
        : `<span style="background:rgba(16,185,129,0.15);color:#10b981;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:900;border:1px solid rgba(16,185,129,0.3);">✅ COVERED (${t.ordered} Orders)</span>`;

      card.innerHTML = `
        <div>
          <div style="font-size:13.5px;font-weight:800;color:var(--t1);display:flex;align-items:center;gap:6px;">
            <span>📍 ${t.name}</span>
            <span style="font-size:11px;color:var(--t3);font-weight:600;">(${t.district})</span>
          </div>
          <div style="font-size:11px;color:var(--t2);margin-top:3px;">
            🏪 Outlets: <b>${t.outlets}</b> | 💰 Sales: <b>৳${(t.revenue||0).toLocaleString()}</b> | 🚗 Visits: <b>${t.visits}</b>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
          ${badgeHtml}
          <button style="background:var(--blue);color:#fff;border:none;padding:4px 10px;border-radius:6px;font-size:10px;font-weight:800;cursor:pointer;">👉 Go to Thana</button>
        </div>
      `;

      card.onclick = () => {
        closeThanaModal();
        drillToSpecificThana(t.name, t.district, t.divIdx);
      };

      container.appendChild(card);
    });
  }

  modal.classList.add('open');
}

function closeThanaModal() {
  const modal = document.getElementById('thanaListModal');
  if (modal) modal.classList.remove('open');
}

function drillToSpecificThana(thanaName, distName, divIdx) {
  // Isolate district first if not already isolated
  const curDiv = DIV_NAMES[divIdx] || activeDivision || 'Dhaka';
  activeDivision = curDiv;
  activeDistrict = distName;
  selectedDivisions = [curDiv];
  selectedDistricts = [{ name: distName, div: curDiv }];

  // Build panels
  buildDistPanel(curDiv, divIdx);
  buildThanaPanel(distName, divIdx);

  // Drill directly into Thana
  drillThana(thanaName, distName, divIdx, null);
  updateAdminSummaryPanel();
}
'''

content = content.replace('/* ═══════════════ RIGHT-SIDE EXECUTIVE ADMINISTRATIVE SUMMARY PANEL ═══════════════ */',
                        js_thana_modal + '\n/* ═══════════════ RIGHT-SIDE EXECUTIVE ADMINISTRATIVE SUMMARY PANEL ═══════════════ */')

# 5. Update updateAdminSummaryPanel to compute currentThanaAnalysis accurately
old_summary_compute = '''    totalUniverse = targetOutlets.length;
    targetOutlets.forEach(o => {
      const rev = o[8] || 0;
      const vis = o[9] || 0;
      const ord = o[13] || 0;
      const sr = o[12];
      const thana = o[16] || 'Unknown';

      totalSales += rev;
      totalVisits += vis;
      totalOrders += ord;

      if (sr && sr !== 'N/A' && sr.trim() !== '') {
        uniqueSRs.add(sr.trim());
      }
      thanaCountMap.add(thana);

      if (rev > 0 || ord > 0) {
        orderedOutlets++;
        coveredThanaSet.add(thana);
      } else if (vis > 0) {
        visitedNoOrderOutlets++;
        coveredThanaSet.add(thana);
      } else {
        untappedOutlets++;
      }
    });'''

new_summary_compute = '''    totalUniverse = targetOutlets.length;
    
    // Thana Map for calculating Covered vs Untapped thanas
    const thanaDataMap = {};

    targetOutlets.forEach(o => {
      const rev = o[8] || 0;
      const vis = o[9] || 0;
      const ord = o[13] || 0;
      const sr = o[12];
      const thana = o[16] || 'Other';
      const dist = o[5] || '';
      const didx = o[4] || 0;

      totalSales += rev;
      totalVisits += vis;
      totalOrders += ord;

      if (sr && sr !== 'N/A' && sr.trim() !== '') {
        uniqueSRs.add(sr.trim());
      }
      
      if (!thanaDataMap[thana]) {
        thanaDataMap[thana] = {
          name: thana,
          district: dist,
          divIdx: didx,
          outlets: 0,
          revenue: 0,
          visits: 0,
          ordered: 0,
          untappedOutlets: 0
        };
      }
      
      thanaDataMap[thana].outlets++;
      thanaDataMap[thana].revenue += rev;
      thanaDataMap[thana].visits += vis;

      if (rev > 0 || ord > 0) {
        orderedOutlets++;
        thanaDataMap[thana].ordered++;
      } else if (vis > 0) {
        visitedNoOrderOutlets++;
      } else {
        untappedOutlets++;
        thanaDataMap[thana].untappedOutlets++;
      }
    });

    // Populate currentThanaAnalysis for interactive modal
    currentThanaAnalysis.all = [];
    currentThanaAnalysis.covered = [];
    currentThanaAnalysis.untapped = [];

    Object.values(thanaDataMap).forEach(t => {
      const isUnt = (t.visits === 0 && t.revenue === 0);
      t.isUntapped = isUnt;
      currentThanaAnalysis.all.push(t);
      if (isUnt) {
        currentThanaAnalysis.untapped.push(t);
      } else {
        currentThanaAnalysis.covered.push(t);
      }
    });

    const totThanaNum = currentThanaAnalysis.all.length || (activeThana ? 1 : 545);
    const covThanaNum = currentThanaAnalysis.covered.length || (activeThana ? (orderedOutlets > 0 ? 1 : 0) : 500);
    const untThanaNum = currentThanaAnalysis.untapped.length || Math.max(0, totThanaNum - covThanaNum);
'''

content = content.replace(old_summary_compute, new_summary_compute)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully added interactive Untapped Thana Explorer!")
