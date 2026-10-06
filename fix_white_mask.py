"""
Set inverse country mask to pure crisp white (#ffffff) across all maps and default to light executive theme
"""

def fix_ceo_map():
    path = r'd:\ITL FINAL ADV ANALYSIS\ceo_national_map.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Set isDark = false
    content = content.replace('let healthFilter = \'ALL\', subTierFilter = \'ALL\', heatOn = false, isDark = true;',
                              'let healthFilter = \'ALL\', subTierFilter = \'ALL\', heatOn = false, isDark = false;')

    # 2. Set renderInverseMask to always use solid white by default
    old_mask_render = '''function renderInverseMask() {
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
}'''

    new_mask_render = '''function renderInverseMask() {
  if (!maskLayer || !map) return;
  maskLayer.clearLayers();
  if (typeof BD_INVERSE_MASK !== 'undefined') {
    const maskPoly = L.geoJSON(BD_INVERSE_MASK, {
      interactive: false,
      pane: 'maskPane',
      style: () => ({
        fillColor: isDark ? '#0b0f19' : '#ffffff',
        fillOpacity: 1.0,
        color: isDark ? '#1e293b' : '#e2e8f0',
        weight: 1.5,
        opacity: 1.0
      })
    });
    maskLayer.addLayer(maskPoly);
  }
}'''

    content = content.replace(old_mask_render, new_mask_render)

    # 3. Ensure map wrapper background is white in light mode
    content = content.replace('--map-bg:#c8d8f0;', '--map-bg:#ffffff;')
    content = content.replace('--map-bg:#0d1627;', '--map-bg:#ffffff;')

    # 4. Remove dark filter inverter on tiles
    content = content.replace(
        '[data-theme="dark"] .leaflet-layer { filter: brightness(0.72) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.7); }',
        '/* Natural street tiles */ .leaflet-layer { filter: none; }'
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("ceo_national_map.html updated to pure white background mask!")

def fix_cluster_map():
    for fpath in [r'd:\ITL FINAL ADV ANALYSIS\cluster_map.html', r'd:\ITL FINAL ADV ANALYSIS\itl_retail_footprint_cluster_map.html']:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace("fillColor: document.documentElement.getAttribute('data-theme') === 'dark' ? '#0b0f19' : '#ffffff'", "fillColor: '#ffffff'")
        content = content.replace("color: '#cbd5e1'", "color: '#e2e8f0'")

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
    print("cluster_map.html updated to pure white background mask!")

if __name__ == '__main__':
    fix_ceo_map()
    fix_cluster_map()
