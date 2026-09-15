import re

html_path = 'ceo_national_map.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CSS
css_additions = """
.kv.zv{color:#c084fc;} .kv.zr{color:#f43f5e;}
.fb.fzv{border-color:#a855f7;color:#c084fc;background:rgba(168,85,247,.18);font-weight:900;}
.fb.fzr{border-color:#f43f5e;color:#fb7185;background:rgba(244,63,94,.18);font-weight:900;}
.st-btn.zv-act{background:#a855f7;border-color:#a855f7;color:#fff;font-weight:900;}
.st-btn.zr-act{background:#f43f5e;border-color:#f43f5e;color:#fff;font-weight:900;}
.cluster-zv{background:#a855f7;color:#fff;box-shadow:0 0 16px rgba(168,85,247,0.85);}
.cluster-zr{background:#f43f5e;color:#fff;box-shadow:0 0 16px rgba(244,63,94,0.85);}
.dcard[data-d="Dhaka"].sel-zv, .dcard.sel-zv{background:rgba(168,85,247,.16)!important;border-color:#a855f7!important;box-shadow:0 0 16px rgba(168,85,247,.3)!important;}
.dcard[data-d="Dhaka"].sel-zr, .dcard.sel-zr{background:rgba(244,63,94,.16)!important;border-color:#f43f5e!important;box-shadow:0 0 16px rgba(244,63,94,.3)!important;}
.fb-section-ttl{font-size:8.5px;text-transform:uppercase;letter-spacing:1px;font-weight:800;color:var(--t3);margin-top:6px;margin-bottom:4px;}
"""

# Insert CSS before </style>
html = html.replace('</style>', css_additions + '\n</style>')

# 2. Update Header KPIs
header_kpi_old = """  <div class="kpis" id="kpiRow">
    <div class="kpi" onclick="setF('ALL')"><span class="kl">Total Filtered</span><span class="kv bl" id="kTotal">—</span></div>
    <div class="kpi" onclick="setF('G')"><span class="kl">🟢 Strong (3-Tier)</span><span class="kv gr" id="kStrong">—</span></div>
    <div class="kpi" onclick="setF('Y')"><span class="kl">🟡 Moderate (3-Tier)</span><span class="kv am" id="kMod">—</span></div>
    <div class="kpi" onclick="setF('R')"><span class="kl">🔴 Weak (3-Tier)</span><span class="kv rd" id="kWeak">—</span></div>
    <div class="kpi"><span class="kl">4M Revenue</span><span class="kv" id="kRev">—</span></div>
    <div class="kpi"><span class="kl">Field Visits</span><span class="kv" id="kVis">—</span></div>
  </div>"""

header_kpi_new = """  <div class="kpis" id="kpiRow">
    <div class="kpi" onclick="setF('ALL')"><span class="kl">Total Outlets</span><span class="kv bl" id="kTotal">—</span></div>
    <div class="kpi" onclick="setF('G')"><span class="kl">🟢 Strong</span><span class="kv gr" id="kStrong">—</span></div>
    <div class="kpi" onclick="setF('Y')"><span class="kl">🟡 Moderate</span><span class="kv am" id="kMod">—</span></div>
    <div class="kpi" onclick="setF('R')"><span class="kl">🔴 Weak</span><span class="kv rd" id="kWeak">—</span></div>
    <div class="kpi" onclick="setF('ZV')" style="border-color:rgba(168,85,247,.3);"><span class="kl" style="color:#c084fc;">🚫 0-Visits (4M)</span><span class="kv zv" id="kZeroVis">—</span></div>
    <div class="kpi" onclick="setF('ZR')" style="border-color:rgba(244,63,94,.3);"><span class="kl" style="color:#fb7185;">💸 0-Revenue (4M)</span><span class="kv zr" id="kZeroRev">—</span></div>
    <div class="kpi"><span class="kl">4M Revenue</span><span class="kv" id="kRev">—</span></div>
    <div class="kpi"><span class="kl">Field Visits</span><span class="kv" id="kVis">—</span></div>
  </div>"""

html = html.replace(header_kpi_old, header_kpi_new)

# 3. Update Sidebar Filter Box
sidebar_filter_old = """    <div class="sb">
      <div class="sb-hd"><span class="sb-ttl">Primary Health Filter</span></div>
      <div class="fbrow">
        <button class="fb fa" id="fbA" onclick="setF('ALL')">All (281K)</button>
        <button class="fb" id="fbG" onclick="setF('G')">🟢 Strong</button>
        <button class="fb" id="fbY" onclick="setF('Y')">🟡 Moderate</button>
        <button class="fb" id="fbR" onclick="setF('R')">🔴 Weak</button>
      </div>

      <!-- Subtier Pill Box -->
      <div class="subtier-wrap" id="subtierBox">
        <div class="subtier-title" id="subtierTitle">Sub-level Breakdown</div>
        <div class="subtier-btns" id="subtierBtns"></div>
      </div>

      <div class="srchw">
        <span class="srchic">🔍</span>
        <input class="srchinp" id="srch" type="text" placeholder="Search outlet name, ID, SR…" oninput="doSearch(this.value)">
      </div>
    </div>"""

sidebar_filter_new = """    <div class="sb">
      <div class="sb-hd"><span class="sb-ttl">Diagnostic Health &amp; Operational Filter</span></div>
      <div class="fb-section-ttl">Health Tiers</div>
      <div class="fbrow">
        <button class="fb fa" id="fbA" onclick="setF('ALL')">All (281K)</button>
        <button class="fb" id="fbG" onclick="setF('G')">🟢 Strong</button>
        <button class="fb" id="fbY" onclick="setF('Y')">🟡 Moderate</button>
        <button class="fb" id="fbR" onclick="setF('R')">🔴 Weak</button>
      </div>

      <div class="fb-section-ttl">Operational Blind Spots (4-Month Window)</div>
      <div class="fbrow">
        <button class="fb" id="fbZV" onclick="setF('ZV')" style="display:flex;align-items:center;justify-content:center;gap:4px;">
          <span>🚫 0-Visits</span> <span id="sbZVCount" style="font-size:8.5px;opacity:0.85;">(72.6k)</span>
        </button>
        <button class="fb" id="fbZR" onclick="setF('ZR')" style="display:flex;align-items:center;justify-content:center;gap:4px;">
          <span>💸 0-Revenue</span> <span id="sbZRCount" style="font-size:8.5px;opacity:0.85;">(72.5k)</span>
        </button>
      </div>

      <!-- Subtier Pill Box -->
      <div class="subtier-wrap" id="subtierBox">
        <div class="subtier-title" id="subtierTitle">Sub-level Breakdown</div>
        <div class="subtier-btns" id="subtierBtns"></div>
      </div>

      <div class="srchw">
        <span class="srchic">🔍</span>
        <input class="srchinp" id="srch" type="text" placeholder="Search outlet name, ID, SR…" oninput="doSearch(this.value)">
      </div>
    </div>"""

html = html.replace(sidebar_filter_old, sidebar_filter_new)

# 4. Update Legend
legend_old = """    <div class="mleg" id="mainLegend">
      <div class="lg" onclick="setF('G')"><div class="lgd g"></div><span class="lgl">🟢 Strong</span></div>
      <div class="lg" onclick="setF('Y')"><div class="lgd y"></div><span class="lgl">🟡 Moderate</span></div>
      <div class="lg" onclick="setF('R')"><div class="lgd r"></div><span class="lgl">🔴 Weak</span></div>
      <div class="lg" id="legWS" style="display:none;" onclick="toggleWhiteSpace()"><span style="font-size:13px;">🎯</span><span class="lgl" style="color:#ff2a85;">White-Space Opportunity</span></div>
    </div>"""

legend_new = """    <div class="mleg" id="mainLegend">
      <div class="lg" onclick="setF('G')"><div class="lgd g"></div><span class="lgl">🟢 Strong</span></div>
      <div class="lg" onclick="setF('Y')"><div class="lgd y"></div><span class="lgl">🟡 Moderate</span></div>
      <div class="lg" onclick="setF('R')"><div class="lgd r"></div><span class="lgl">🔴 Weak</span></div>
      <div class="lg" onclick="setF('ZV')"><div class="lgd" style="background:#a855f7;box-shadow:0 0 10px rgba(168,85,247,.8);"></div><span class="lgl">🚫 0-Visits</span></div>
      <div class="lg" onclick="setF('ZR')"><div class="lgd" style="background:#f43f5e;box-shadow:0 0 10px rgba(244,63,94,.8);"></div><span class="lgl">💸 0-Revenue</span></div>
      <div class="lg" id="legWS" style="display:none;" onclick="toggleWhiteSpace()"><span style="font-size:13px;">🎯</span><span class="lgl" style="color:#ff2a85;">White-Space Opportunity</span></div>
    </div>"""

html = html.replace(legend_old, legend_new)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML structure updated successfully!")
