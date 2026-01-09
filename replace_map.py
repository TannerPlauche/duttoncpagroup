#!/usr/bin/env python3
"""
Replace Mapbox map with Google Maps embed
"""

import re

# Address for the map
address = "409 Airport Rd, Griffin, GA 30224"
# Business name
business = "Dutton CPA Group"

# Google Maps embed HTML
google_maps_embed = f'''<div class="mapContainer google-map" style="height: 400px; width: 100%; overflow: hidden; z-index: 0;">
    <iframe
        width="100%"
        height="100%"
        style="border:0;"
        loading="lazy"
        allowfullscreen
        referrerpolicy="no-referrer-when-downgrade"
        src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q={address.replace(' ', '+')}&zoom=13">
    </iframe>
</div>'''

# Read the contact HTML file
with open('/Users/tannerplauche/source/duttoncavanaugh/public/contact.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Pattern to match the entire mapContainer div
# This matches from <div class="mapContainer mapboxgl-map" to its closing </div>
pattern = r'<div class="mapContainer mapboxgl-map"[^>]*>.*?</div>\s*</div>\s*</div>'

# Replace the Mapbox map with Google Maps
html_updated = re.sub(pattern, google_maps_embed + ' </div></div>', html, flags=re.DOTALL)

# Write back to file
with open('/Users/tannerplauche/source/duttoncavanaugh/public/contact.html', 'w', encoding='utf-8') as f:
    f.write(html_updated)

print("✓ Successfully replaced Mapbox map with Google Maps embed!")
print(f"  Address: {address}")
print(f"  Business: {business}")
