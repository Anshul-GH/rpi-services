import requests
import constants
import re

class TelegramNotifier:
    def __init__(self):
        self.api_url = f"https://api.telegram.org/bot{constants.CC_BOT_TOKEN}/sendMessage"

    def escape_html(self, text):
        """Escape HTML special characters"""
        if not text:
            return "Unknown Product"
        chars = ['&', '<', '>', '"']
        for char in chars:
            text = text.replace(char, f'&#{ord(char)};')
        return text[:100]

    def _get_product_title(self, asin):
        """Extract real product name from Amazon page"""
        try:
            url = f"https://amazon.com/dp/{asin}"
            r = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'
            }, timeout=8)
            
            # Multiple selectors for product title
            title_selectors = [
                r'id=["\']productTitle["\'][^>]*>([^<]+?)<',
                r'"name"\s*:\s*"([^"]+?)"',
                r'<span[^>]*id="productTitle"[^>]*>([^<]+?)</span>'
            ]
            
            for selector in title_selectors:
                match = re.search(selector, r.text, re.IGNORECASE | re.DOTALL)
                if match:
                    title = re.sub(r'\s+', ' ', match.group(1).strip())
                    return self.escape_html(title)
            
            return f"Top Drop ASIN {asin}"
            
        except Exception as e:
            print(f"⚠️ Title fetch failed for {asin}: {e}")
            return f"Top Drop ASIN {asin}"

    def send_alert(self, deal, price):
        """Send formatted Telegram alert for ALL deals"""
        try:
            asin = deal['asin']
            product_title = self._get_product_title(asin)
            
            text = f"""
🚨 *CamelCamelCamel TOP DROP DETECTED* 🚨

*{product_title}*

📦 *ASIN*: `{asin}`
💰 *Amazon Price*: {price}
🛒 *Buy*: {deal['amazon_url']}
📉 *Camel Chart*: {deal['camel_url']}

#camelintel #arbitrage
            """.strip()

            print(f"📤 Sending to chat {constants.CC_CHAT_ID}...")
            response = requests.post(self.api_url, data={
                'chat_id': constants.CC_CHAT_ID,
                'text': text,
                'parse_mode': 'Markdown',  # Fixed: Use Markdown (more reliable)
                'disable_web_page_preview': 'false'
            }, timeout=10)

            print(f"📥 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Alert: {asin} ({product_title[:40]})")
            else:
                print(f"❌ Telegram: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")
