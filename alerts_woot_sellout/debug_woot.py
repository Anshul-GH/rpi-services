#!/usr/bin/env python3

import subprocess
import re

print("🔍 Fetching Woot page...")

cmd = [
    'curl', '-s',
    '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'https://www.woot.com/category/sellout'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
html = result.stdout

print(f"\n📊 HTML Length: {len(html)} characters")
print(f"\n{'='*60}")
print("First 2000 characters:")
print(html[:2000])
print(f"\n{'='*60}")

# Look for common patterns
print("\n🔍 Looking for patterns...")

# Pattern 1: offer links
offers = re.findall(r'offer[s]?/[a-zA-Z0-9-]+', html)
print(f"\n📌 Found 'offer' mentions: {len(offers)}")
if offers:
    print(f"   Examples: {offers[:5]}")

# Pattern 2: product links
products = re.findall(r'href="([^"]*woot[^"]*)"', html)
print(f"\n📌 Found hrefs with 'woot': {len(products)}")
if products:
    print(f"   Examples: {products[:5]}")

# Pattern 3: JSON-LD
jsonld = re.findall(r'<script type="application/ld\+json">(.+?)</script>', html, re.DOTALL)
print(f"\n📌 Found JSON-LD scripts: {len(jsonld)}")

# Pattern 4: Look for any script tags with product data
scripts = re.findall(r'<script[^>]*>(.{0,200})', html)
print(f"\n📌 Found script tags: {len(scripts)}")

# Pattern 5: Data attributes
data_attrs = re.findall(r'data-[a-z-]+=', html)
print(f"\n📌 Found data attributes: {len(set(data_attrs))}")
if data_attrs:
    print(f"   Unique: {list(set(data_attrs))[:10]}")

# Save full HTML for inspection
with open('/tmp/woot_debug.html', 'w') as f:
    f.write(html)
print(f"\n💾 Saved full HTML to: /tmp/woot_debug.html")
print(f"   View with: cat /tmp/woot_debug.html | less")
