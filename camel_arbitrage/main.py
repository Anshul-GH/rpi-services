#!/usr/bin/env python3
import sys, os
sys.path.insert(0, '.')
from camel_arbitrage.core import ArbitrageScanner
from camel_arbitrage.notifier import TelegramNotifier
import constants

print("🚀 Camel Arbitrage v2.0 - Pi3 Ready")
scanner = ArbitrageScanner()
notifier = TelegramNotifier()
scanner.run(notifier)
