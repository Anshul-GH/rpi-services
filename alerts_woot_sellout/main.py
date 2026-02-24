#!/usr/bin/env python3

import sys, os
sys.path.insert(0, '.')

from woot_clearance.core import WootScanner
from woot_clearance.notifier import TelegramNotifier
import constants

print("🚀 Woot Clearance Scanner v1.0 - Pi Ready")

scanner = WootScanner()
notifier = TelegramNotifier()

scanner.run(notifier)
