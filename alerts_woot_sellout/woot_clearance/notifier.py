import requests
import constants

class TelegramNotifier:
    def __init__(self):
        self.api_url = f"https://api.telegram.org/bot{constants.WOOT_BOT_TOKEN}/sendMessage"

    def send_alert(self, deal):
        """Send Woot URL with preview"""
        try:
            product_id = deal['id']
            woot_url = deal['url']
            
            print(f"📤 Sending Woot URL: {woot_url}")
            
            payload = {
                'chat_id': constants.WOOT_CHAT_ID,
                'text': woot_url,
                'disable_web_page_preview': False,
                'disable_notification': False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Sent: {woot_url}")
            else:
                print(f"❌ Telegram error [{response.status_code}]: {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending {deal.get('id', 'unknown')}: {e}")
