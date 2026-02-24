# Woot Clearance Deal Scanner

Automated deal monitoring system that scrapes Woot.com clearance deals and sends Telegram notifications for new products.

## Features

- 🔍 **Scrapes Woot sellout page** using curl (no Selenium needed)
- 📱 **Telegram notifications** with link previews
- 🎲 **Random scan intervals** (45-120 minutes) to avoid detection patterns
- 💾 **Tracks seen deals** to avoid duplicate notifications
- 🔄 **Auto-restart** systemd service for reliability
- 🔒 **File locking** prevents race conditions

## Architecture

