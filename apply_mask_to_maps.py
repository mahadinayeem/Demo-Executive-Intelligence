"""
Inject bd_mask.js and renderInverseMask into ceo_national_map.html and cluster_map.html
"""
import re

def patch_ceo_map():
    path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add script tag in head
    if '<script src="bd_mask.js"></script>' not in content:
        content = content.replace('<script src="bd_geo.js"></script>', '<script src="bd_mask.js"></script>\n<script src="bd_geo.js"></script>')

    # 2. Add maskLayer variable
    if 'let maskLayer;' not in content and 'let maskLayer = null;' not in content:
        content = content.replace('let activeDivision = null', 'let maskLayer = null;\nlet activeDivision = null')

    # 3. Add custom mask pane and maskLayer in DOMContentLoaded
    old_init = '''  // Base Map Layer (Default Google Streets)
  setBaseLayer('google_streets');

  polyLayer = L.layerGroup().addTo(map);'''

    new_init = '''  // Base Map Layer (Default Google Streets)
  setBaseLayer('google_streets');

  // Create dedicated pane for Bangladesh inverse country mask (above tiles, below polygons)
  map.createPane('maskPane');
  map.getPane('maskPane').style.zIndex = 300;
  map.getPane('maskPane').style.pointerEvents = 'none';

  maskLayer = L.layerGroup().addTo(map);
  renderInverseMask();

  polyLayer = L.layerGroup().addTo(map);'''

    if old_init in content:
        content = content.replace(old_init, new_init)

    # 4. Add renderInverseMask function
    mask_fn = '''
/* ═══════════════ BANGLADESH INVERSE COUNTRY MASK (HIDES FOREIGN TERRITORY) ═══════════════ */
function renderInverseMask() {
  if (!maskLayer || !map) return;
  maskLayer.clearLayers();
  if (typeof BD_INVERSE_MASK !== 'undefined') {
    const maskPoly = L.geoJSON(BD_INVERSE_MASK, {
      interactive: false,
      pane: 'maskPane',
      style: () => ({
        fillColor: isDark ? '#07090f' : '#ffffff',
        fillOpacity: 1.0,
        color: isDark ? '#334155' : '#cbd5e1',
        weight: 1.5,
        opacity: 0.9
      })
    });
    maskLayer.addLayer(maskPoly);
  }
}
'''
    if 'function renderInverseMask()' not in content:
        content = content.replace('function setBaseLayer(type) {', mask_fn + '\nfunction setBaseLayer(type) {')

    # 5. In toggleTheme(), update mask color
    content = content.replace('function toggleTheme() {', 'function toggleTheme() {\n  setTimeout(renderInverseMask, 50);')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("ceo_national_map.html patched with Inverse Country Mask!")

def patch_cluster_map():
    path = r'd:\ITL FINAL ADV ANALYSIS\cluster_map.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if '<script src="bd_mask.js"></script>' not in content:
        content = content.replace('<script src="bd_geo.js"></script>', '<script src="bd_mask.js"></script>\n<script src="bd_geo.js"></script>')

    if 'renderInverseMask' not in content:
        init_marker = "L.control.zoom({ position: 'bottomright' }).addTo(map);"
        mask_addition = """L.control.zoom({ position: 'bottomright' }).addTo(map);
  map.createPane('maskPane');
  map.getPane('maskPane').style.zIndex = 300;
  map.getPane('maskPane').style.pointerEvents = 'none';

  const maskLayer = L.layerGroup().addTo(map);
  if (typeof BD_INVERSE_MASK !== 'undefined') {
    L.geoJSON(BD_INVERSE_MASK, {
      interactive: false,
      pane: 'maskPane',
      style: () => ({
        fillColor: document.documentElement.getAttribute('data-theme') === 'dark' ? '#0b0f19' : '#ffffff',
        fillOpacity: 1.0,
        color: '#cbd5e1',
        weight: 1.5
      })
    }).addTo(maskLayer);
  }"""
        content = content.replace(init_marker, mask_addition)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    with open(r'd:\ITL FINAL ADV ANALYSIS\itl_retail_footprint_cluster_map.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("cluster_map.html and itl_retail_footprint_cluster_map.html patched with Inverse Country Mask!")

if __name__ == '__main__':
    patch_ceo_map()
    patch_cluster_map()
