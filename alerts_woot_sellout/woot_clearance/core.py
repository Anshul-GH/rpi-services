#!/home/piblack/projects/woot-clearance/.venv/bin/python

import re, time, os, subprocess, fcntl, random
from datetime import datetime, timedelta
import sys

sys.path.insert(0, os.path.dirname(__file__) + "/..")
import constants

class WootScanner:
    def __init__(self):
        self.seen_file = constants.SEEN_FILE
        self.seen_ids = self._load_seen()

    def _load_seen(self):
        seen = set()
        try:
            if os.path.exists(self.seen_file):
                with open(self.seen_file) as f:
                    for line in f:
                        product_id = line.strip()
                        if product_id:
                            seen.add(product_id)
                print(f"✅ Loaded {len(seen)} Woot IDs from seen file")
        except:
            pass
        return seen

    def _save_seen(self):
        try:
            # Atomic append with file locking
            with open(self.seen_file, 'a') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.seek(0, os.SEEK_END)
                new_ids = self.seen_ids - set(line.strip() for line in open(self.seen_file) if line.strip())
                for product_id in sorted(new_ids):
                    f.write(product_id + '\n')
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            print(f"⚠️ Save error: {e}")

    def _get_random_interval(self):
        """Generate random interval between min and max"""
        interval = random.randint(constants.POLL_INTERVAL_MIN, constants.POLL_INTERVAL_MAX)
        return interval

    def parse_woot_page(self):
        """Scrape Woot sellout page using curl"""
        try:
            print(f"🔍 Fetching Woot sellout page...")
            
            cmd = [
                'curl', '-s',
                '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                '-H', 'Accept-Language: en-US,en;q=0.5',
                constants.WOOT_SELLOUT_URL
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            html = result.stdout
            
            if not html or len(html) < 1000:
                print(f"⚠️ Empty or invalid response from Woot")
                return []
            
            deals = []
            
            # Updated pattern: offers/product-slug format
            # Example: offers/amazon-basics-ultra-premium-wireless-combo-1
            offer_pattern = r'offers/([a-zA-Z0-9-]+)'
            offer_slugs = re.findall(offer_pattern, html)
            
            print(f"✅ Found {len(offer_slugs)} offer mentions")
            
            # Dedupe and create deals
            unique_slugs = list(set(offer_slugs))
            
            for slug in unique_slugs:
                product_url = f"https://www.woot.com/offers/{slug}"
                
                deals.append({
                    'id': slug,
                    'title': slug.replace('-', ' ').title()[:100],
                    'url': product_url
                })
            
            print(f"✅ Parsed {len(deals)} unique Woot deals")
            return deals
            
        except subprocess.TimeoutExpired:
            print(f"⚠️ Timeout fetching Woot page")
            return []
        except Exception as e:
            print(f"⚠️ Error parsing Woot: {e}")
            import traceback
            traceback.print_exc()
            return []

    def run(self, notifier):
        while True:
            print(f"\n{'='*50}")
            print(f"WOOT SCAN @ {datetime.now().strftime('%H:%M:%S')}")
            
            deals = self.parse_woot_page()
            
            if deals:
                # Filter new deals
                new_deals = [d for d in deals if d['id'] not in self.seen_ids]
                
                if new_deals:
                    print(f"🚨 {len(new_deals)} NEW WOOT DEALS!")
                    
                    # Send each deal as a separate message
                    for deal in new_deals:
                        notifier.send_alert(deal)
                        time.sleep(constants.MESSAGE_DELAY)
                    
                    # Add to seen and save
                    for deal in new_deals:
                        self.seen_ids.add(deal['id'])
                    self._save_seen()
                else:
                    print("ℹ️ No new Woot deals")
            else:
                print("ℹ️ No deals parsed")
            
            # Calculate random interval for next scan
            next_interval = self._get_random_interval()
            next_scan_time = datetime.now() + timedelta(seconds=next_interval)
            
            print(f"⏱️ Next scan in {next_interval}s ({next_interval//60} mins)")
            print(f"🕐 Next scan at: {next_scan_time.strftime('%H:%M:%S')}")
            
            time.sleep(next_interval)

if __name__ == "__main__":
    from woot_clearance.notifier import TelegramNotifier
    notifier = TelegramNotifier()
    scanner = WootScanner()
    scanner.run(notifier)
