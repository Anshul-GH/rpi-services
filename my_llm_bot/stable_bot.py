#!/usr/bin/env python3

"""
Pi 3 SERVICE CONTROL BOT - FIXED SERVICE PARSING
Handles both 'camel-poller' and 'camel-poller.service'
"""

import telebot
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

SERVICES = [
    "sd-rss-poller.service",
    "camel-poller.service",
    "amazon-price-tracker.service"
]

def run_sudo_cmd(cmd_list):
    """Run sudo command with full paths"""
    full_cmd = ["/usr/bin/sudo"] + cmd_list
    return subprocess.getoutput(" ".join(full_cmd))

# def get_all_status():
#     """Get service status without sudo"""
#     status_lines = []
#     for service in SERVICES:
#         result = subprocess.getoutput(f'/bin/systemctl is-active {service}')
#         status = "🟢 active" if "active" in result else "🔴 inactive"
#         status_lines.append(f"{service}: {status}")
#     return "📋 SERVICE STATUS:\n" + "\n".join(status_lines)

def get_all_status():
    status_lines = []
    for service in SERVICES:
        result = subprocess.getoutput(f'/bin/systemctl is-active {service} 2>/dev/null')
        result = result.strip()
        if result == 'active':
            status_lines.append(f"🟢 {service}: active")
        elif result == 'inactive':
            status_lines.append(f"🔴 {service}: inactive")
        elif result == 'unknown':
            status_lines.append(f"⚪ {service}: not installed")
        else:
            status_lines.append(f"❓ {service}: {result}")
    return "📋 SERVICE STATUS:\n" + "\n".join(status_lines)


@bot.message_handler(commands=['start'])
def start(message):
    status = get_all_status()
    bot.reply_to(message, f"🤖 Pi 3 SERVICE BOT\n\n{status}")

@bot.message_handler(commands=['status', 'services'])
def status_cmd(message):
    bot.reply_to(message, get_all_status())

@bot.message_handler(commands=['start', 'stop', 'restart'])
def control(message):
    parts = message.text.split()
    action = parts[0][1:].strip()  # get 'stop' from '/stop'
    
    if len(parts) < 2:
        bot.reply_to(message, f"Usage: /{action} camel-poller")
        return
    
    # FIXED: Handle both with/without .service
    service_input = parts[1].strip()
    if service_input.endswith('.service'):
        service_name = service_input[:-8]  # remove .service
    else:
        service_name = service_input
    
    service = f"{service_name}.service"
    
    # FIXED: Check against service names WITHOUT .service
    valid_names = ['sd-rss-poller', 'camel-poller', 'amazon-price-tracker']
    if service_name not in valid_names:
        bot.reply_to(message, f"❌ Invalid service '{service_name}'\nAvailable: {', '.join(valid_names)}")
        return
    
    result = run_sudo_cmd(["/bin/systemctl", action, service])
    status = subprocess.getoutput(f'/bin/systemctl is-active {service}')
    
    bot.reply_to(message, f"🔧 {action.upper()} {service}\n```\n{result}\nStatus: {status}\n```")

@bot.message_handler(commands=['logs'])
def logs(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /logs camel-poller")
        return
    
    # FIXED: Handle both with/without .service
    service_input = parts[1].strip()
    if service_input.endswith('.service'):
        service_name = service_input[:-8]
    else:
        service_name = service_input
    
    service = f"{service_name}.service"
    
    valid_names = ['sd-rss-poller', 'camel-poller', 'amazon-price-tracker']
    if service_name not in valid_names:
        bot.reply_to(message, f"❌ Invalid service '{service_name}'\nAvailable: {', '.join(valid_names)}")
        return
    
    logs = run_sudo_cmd(["/usr/bin/journalctl", "-u", service, "-n", "10", "--no-pager"])
    bot.reply_to(message, f"📜 {service}\n```\n{logs}\n```")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, """
🤖 Pi 3 SERVICE BOT ✅ FIXED

/status - Show all services
/start camel-poller - Start service  
/stop camel-poller - Stop service
/restart camel-poller - Restart service
/logs camel-poller - Show logs

✅ Works with OR without '.service'
✅ /stop camel-poller ✅ WORKS NOW
✅ /stop camel-poller.service ✅ WORKS NOW

Services: sd-rss-poller, camel-poller, amazon-price-tracker
    """)

@bot.message_handler(func=lambda m: True)
def unknown(message):
    bot.reply_to(message, "Use /help")

if __name__ == "__main__":
    print("🚀 SERVICE BOT STARTED")
    bot.infinity_polling()
