import requests
import constants
import time

class TelegramNotifier:
    def __init__(self):
        self.api_url = f"https://api.telegram.org/bot{constants.CC_BOT_TOKEN}/sendMessage"

    def send_alert(self, deal):
        """Send clean Amazon URL with mandatory preview"""
        try:
            asin = deal['asin']
            amazon_url = f"https://amazon.com/dp/{asin}"
            
            print(f"📤 Sending {amazon_url} to chat {constants.CC_CHAT_ID}...")
            
            # Use json parameter with boolean False for disable_web_page_preview
            payload = {
                'chat_id': constants.CC_CHAT_ID,
                'text': amazon_url,
                'disable_web_page_preview': False,
                'disable_notification': False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Sent: {amazon_url}")
                print(f"⏳ Waiting {constants.MESSAGE_DELAY}s for preview generation...")
                time.sleep(constants.MESSAGE_DELAY)  # Delay to allow preview to load
            else:
                print(f"❌ Telegram error [{response.status_code}]: {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending {deal.get('asin', 'unknown')}: {e}")
