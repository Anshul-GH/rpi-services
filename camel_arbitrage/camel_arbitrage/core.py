#!/home/piblack/projects/camel-arbitrage/.venv/bin/python

import re, time, os, requests, subprocess, fcntl
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(__file__) + "/..")

import constants

class ArbitrageScanner:
    def __init__(self):
        self.seen_file = constants.SEEN_FILE
        self.seen_asins = self._load_seen()

    def _load_seen(self):
        seen = set()
        try:
            if os.path.exists(self.seen_file):
                with open(self.seen_file) as f:
                    for line in f:
                        asin = line.strip()
                        if asin.startswith('B') and len(asin) == 10:
                            seen.add(asin)
                print(f"✅ Loaded {len(seen)} B-ASINs from seen file")
        except:
            pass
        return seen

    def _save_seen(self):
        try:
            # Atomic append with file locking to prevent race conditions
            with open(self.seen_file, 'a') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX) # Acquire exclusive lock
                f.seek(0, os.SEEK_END) # Ensure append position
                new_asins = self.seen_asins - set(line.strip() for line in open(self.seen_file) if line.strip())
                for asin in sorted(new_asins):
                    f.write(asin + '\n')
                fcntl.flock(f.fileno(), fcntl.LOCK_UN) # Release lock
        except Exception as e:
            print(f"⚠️ Save error: {e}")

    def get_amazon_price(self, asin):
        try:
            url = f"https://amazon.com/dp/{asin}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'}, timeout=8)
            m = re.search(r'["\s]price["\s]*:["\s]*\$?([\d,]+\.?\d*)', r.text)
            return f"${m.group(1)}" if m else "N/A"
        except:
            return "N/A"

    def parse_rss(self):
        try:
            cmd = ['curl', '-s', '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120', 'https://camelcamelcamel.com/top_drops/feed']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            # FIXED: Get ALL unique B-ASINs from RSS, NO LIMIT
            raw_asins = re.findall(r'/product/B([A-Z0-9]{9})', result.stdout)
            asins = list(set(raw_asins))  # Dedupe ONLY, no [:5] limit!
            
            print(f"🔍 Raw ASINs found: {len(raw_asins)}, unique: {len(asins)}")
            
            deals = []
            for asin in asins:
                full_asin = 'B' + asin
                print(f"✅ Processing B-ASIN: {full_asin}")
                deals.append({
                    'asin': full_asin,
                    'title': f"Top Drop: {full_asin}",
                    'amazon_url': f"https://amazon.com/dp/{full_asin}",
                    'camel_url': f"https://camelcamelcamel.com/product/{full_asin}"
                })
            
            print(f"✅ Parsed {len(deals)} unique B-ASIN deals from RSS")
            return deals
            
        except Exception as e:
            print(f"⚠️ CURL error: {e}")
            return []

    def run(self, notifier):
        while True:
            print(f"\n{'='*50}")
            print(f"SCAN @ {datetime.now().strftime('%H:%M:%S')}")
            
            deals = self.parse_rss()
            
            if deals:
                # Filter new deals against seen set
                new_deals = [d for d in deals if d['asin'] not in self.seen_asins]
                
                if new_deals:
                    print(f"🚨 {len(new_deals)} NEW B-ASIN DEALS!")
                    for deal in new_deals:
                        price = self.get_amazon_price(deal['asin'])
                        notifier.send_alert(deal, price)
                    
                    # Add to seen and save ATOMICALLY
                    for deal in new_deals:
                        self.seen_asins.add(deal['asin'])
                    self._save_seen()
                else:
                    print("ℹ️ No new B-ASIN deals")
            else:
                print("ℹ️ No deals parsed")
            
            print(f"⏱️ Next in {constants.POLL_INTERVAL}s")
            time.sleep(constants.POLL_INTERVAL)

if __name__ == "__main__":
    from camel_arbitrage.notifier import TelegramNotifier
    notifier = TelegramNotifier()
    scanner = ArbitrageScanner()
    scanner.run(notifier)
