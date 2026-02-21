#!/usr/bin/env python3
"""
CamelCamelCamel Top Drops - DIRECT XML PARSING
Uses your exact RSS XML structure with proper endpoint
"""

import re
import time
import os
import random
from datetime import datetime
import requests
from xml.etree import ElementTree as ET

import sys
sys.stdout.reconfigure(encoding='utf-8', write_through=True)
import constants as const

TIMEFORMAT = '%Y-%m-%d %H:%M:%S'

RSS_URL = 'https://camelcamelcamel.com/rss'  # Base RSS - adjust if needed

def load_seen_urls() -> set:
    seen = set()
    if os.path.exists(const.SEEN_FILE):
        with open(const.SEEN_FILE, 'r') as f:
            for line in f:
                asin = line.strip()
                if re.fullmatch(r'[A-Z0-9]{10}', asin):
                    seen.add(asin)
        print(f"✅ Loaded {len(seen)} seen ASINs")
    return seen

def save_seen_urls(seen: set):
    with open(const.SEEN_FILE, 'w') as f:
        for asin in sorted(seen):
            f.write(asin + '\n')

def parse_camel_xml() -> list:
    """Parse your exact RSS XML structure"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        print(f"📡 Fetching RSS...")
        r = requests.get(RSS_URL, headers=headers, timeout=15)
        print(f"Status: {r.status_code}")
        
        if r.status_code != 200:
            return []
            
        # Parse XML directly (like your sample)
        root = ET.fromstring(r.content)
        deals = []
        
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            
            # Extract ASIN from Camel link: /product/B0XXXXXXX
            asin_match = re.search(r'/product/([A-Z0-9]{10})', link)
            if not asin_match:
                continue
                
            asin = asin_match.group(1)
            
            # Amazon link from description (your exact format)
            desc = item.find('description').text if item.find('description') is not None else ''
            amazon_match = re.search(r'<a href="([^"]*/go)">Amazon\.com</a>', desc)
            amazon_url = amazon_match.group(1) if amazon_match else f"https://amazon.com/dp/{asin}"
            
            deals.append({
                'asin': asin,
                'title': title[:120],
                'amazon_url': amazon_url,
                'camel_url': link
            })
            
        print(f"✅ Parsed {len(deals)} deals")
        return deals
        
    except Exception as e:
        print(f"❌ Parse error: {e}")
        return []

def notify_new_telegram(deals: list):
    api_url = f"https://api.telegram.org/bot{const.CC_BOT_TOKEN}/sendMessage"
    
    for deal in deals:
        text = f"""🚨 NEW CAMEL TOP DROP!

**{deal['title']}**

🛒 [Amazon]({deal['amazon_url']})
📊 [Camel]({deal['camel_url']})

`{deal['asin']}`"""
        
        try:
            requests.post(api_url, data={
                'chat_id': const.CC_CHAT_ID,
                'text': text.replace('_', '\\_'),
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }, timeout=10)
            print(f"✅ Telegram: {deal['asin']}")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Telegram: {e}")

def main():
    print("🚀 CamelCamelCamel XML Monitor")
    seen_asins = load_seen_urls()
    
    while True:
        print(f"\n{'='*60}")
        print(f"SCAN @ {datetime.now().strftime(TIMEFORMAT)}")
        
        deals = parse_camel_xml()
        
        if deals:
            new_deals = [d for d in deals if d['asin'] not in seen_asins]
            if new_deals:
                print(f"🚨 {len(new_deals)} NEW DEALS!")
                notify_new_telegram(new_deals)
                for deal in new_deals:
                    seen_asins.add(deal['asin'])
                save_seen_urls(seen_asins)
            else:
                print("ℹ️ No new deals")
        else:
            print("⚠️ No RSS data")
            
        print(f"⏱️ Next in {const.POLL_INTERVAL}s (seen: {len(seen_asins)})")
        time.sleep(const.POLL_INTERVAL)

if __name__ == "__main__":
    main()
