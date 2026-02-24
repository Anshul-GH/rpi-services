#!/usr/bin/env python3

# Woot Telegram Bot
WOOT_BOT_TOKEN = ""
WOOT_CHAT_ID = ""

# Woot scanning settings - RANDOM INTERVALS
POLL_INTERVAL_MIN = 2700  # 45 minutes (45 * 60)
POLL_INTERVAL_MAX = 7200  # 2 hours (120 * 60)

SEEN_FILE = "/home/piblack/projects/woot-clearance/seen_woot_ids.txt"
WOOT_SELLOUT_URL = "https://www.woot.com/category/sellout"

# Delay between Telegram messages to ensure previews load
MESSAGE_DELAY = 3
