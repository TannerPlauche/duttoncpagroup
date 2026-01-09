#!/usr/bin/env python3
"""
Update Google Maps embed with new address
"""

import re

# New address
new_address = "124 N Hill St, Griffin, GA 30223"
business = "Dutton CPA Group"

# New Google Maps embed HTML
google_maps_embed = f'''<div class="mapContainer google-map" style="height: 400px; width: 100%; overflow: hidden; z-index: 0;">
    <iframe
        width="100%"
        height="100%"
        style="border:0;"
        loading="lazy"
        allowfullscreen
        referrerpolicy="no-referrer-when-downgrade"
        src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q={new_address.replace(' ', '+')}&zoom=15">
    </iframe>
</div>'''

# Read the contact HTML file
with open('/Users/tannerplauche/source/duttoncavanaugh/public/contact.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Pattern to match the Google Maps embed
pattern = r'<div class="mapContainer google-map"[^>]*>.*?</iframe>\s*</div>'

# Replace with updated map
html_updated = re.sub(pattern, google_maps_embed, html, flags=re.DOTALL)

# Write back to file
with open('/Users/tannerplauche/source/duttoncavanaugh/public/contact.html', 'w', encoding='utf-8') as f:
    f.write(html_updated)

print("✓ Successfully updated Google Maps embed!")
print(f"  New Address: {new_address}")
print(f"  Business: {business}")
