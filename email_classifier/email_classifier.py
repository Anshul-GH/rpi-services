#!/usr/bin/env python3
"""
Pi 3 Email Spam Classifier - PRODUCTION READY
Postfix → /var/mail/piblack → ~/mail_junk.txt + ~/mail_archive.txt → Telegram
"""

import email
import os
import re
import logging
from datetime import datetime
import asyncio
from telegram import Bot
from telegram.error import TelegramError

# CONFIGURATION
MAIL_FILE = '/var/mail/piblack'
BOT_TOKEN = "8021538092:AAH7fPQMMrxXPl0A3LahbfoGWEeNO-9ZLx0"
CHAT_ID = "7574355748"
JUNK_FILE = '/home/piblack/mail_junk.txt'
ARCHIVE_FILE = '/home/piblack/mail_archive.txt'

# 1. EXPANDED KEYWORDS (add these)
SPAM_KEYWORDS = [
    # Original
    'viagra', 'casino', 'lottery', 'free money', 'click here', 'unsubscribe',
    'dear customer', 'winner', 'congratulations', 'free viagra', 'win cash',
    'casino bonus', 'double money', 'limited offer', 'urgent offer',
    
    # NEW: Modern spam patterns
    'bitcoin', 'crypto', 'your package', 'delivery failed', 'account suspended',
    'verify account', 'update payment', 'security alert', 'claim reward',
    'your order', 'tracking number', 'invoice attached', 'urgent action required',
    '0', 'claim now', 'limited time', 'exclusive offer', 'get started now'
]

logging.basicConfig(
    filename='/home/piblack/projects/email-bot/emailbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# 2. BETTER TEXT EXTRACTION
def preprocess_email(msg):
    """Extract ALL text content"""
    text_parts = []
    
    # Subject
    subject = msg.get('Subject', '').lower()
    text_parts.append(subject)
    
    # Walk through all parts (HTML, attachments, etc.)
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ['text/plain', 'text/html']:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        text_parts.append(payload.decode(errors='ignore').lower())
                except:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                text_parts.append(payload.decode(errors='ignore').lower())
        except:
            pass
    
    full_text = ' '.join(text_parts)
    return re.sub(r'\s+', ' ', full_text).strip()

# 3. DEBUGGING - ADD THIS to see what's happening
def is_spam(text):
    """Enhanced spam detection with DEBUG"""
    print(f"🔍 Scanning: {text[:200]}...")
    text_lower = text.lower()
    
    for keyword in SPAM_KEYWORDS:
        if keyword.lower() in text_lower:
            print(f"✅ SPAM MATCH: '{keyword}'")
            return True  # Exit immediately on first match
    
    print(f"ℹ️ Scanned {len(SPAM_KEYWORDS)} keywords, 0 matches")
    return False


async def send_telegram_summary(legit_count, spam_count):
    """Send summary to @myemail_assist_bot"""
    try:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        message = f"📧 Email Summary {date_str}\n✅ Legit: {legit_count}\n🗑️ Spam: {spam_count}"
        
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print("✅ Telegram sent!")
        logging.info(f"Telegram: {legit_count} legit, {spam_count} spam")
        
    except Exception as e:
        print(f"❌ Telegram failed: {e}")
        logging.error(f"Telegram error: {e}")

def main():
    """Main processing"""
    if not os.path.exists(MAIL_FILE) or os.path.getsize(MAIL_FILE) == 0:
        print("ℹ️  No new emails")
        return
    
    print(f"📧 Processing {os.path.getsize(MAIL_FILE)} bytes...")
    
    with open(MAIL_FILE, 'rb') as f:
        content = f.read()
    
    legit_count = spam_count = 0
    junk_content = b''
    archive_content = b''
    
    # Split mbox emails
    emails = content.split(b'\nFrom ')
    emails = [e for e in emails[1:] if b'Subject:' in e]
    
    print(f"Found {len(emails)} emails")
    
    for i, email_data in enumerate(emails):
        try:
            msg = email.message_from_bytes(b'From ' + email_data)
            subject = msg.get('Subject', 'No Subject')
            text = preprocess_email(msg)
            
            print(f"Email {i+1}: '{subject}' -> {len(text)} chars")
            
            if is_spam(text):
                junk_content += b'\nFrom ' + email_data
                spam_count += 1
                print(f"  🗑️  SPAM: {subject[:50]}")
            else:
                archive_content += b'\nFrom ' + email_data
                legit_count += 1
                print(f"  ✅ LEGIT: {subject[:50]}")
                
        except Exception as e:
            print(f"  ❌ Parse error: {e}")
            continue
    
    # Save sorted emails
    if junk_content:
        with open(JUNK_FILE, 'ab') as f:
            f.write(junk_content)
        print(f"🗑️  Saved {spam_count} spam to {JUNK_FILE}")
    
    if archive_content:
        with open(ARCHIVE_FILE, 'ab') as f:
            f.write(archive_content)
        print(f"✅ Saved {legit_count} legit to {ARCHIVE_FILE}")
    
    # Clear inbox
    open(MAIL_FILE, 'w').close()
    print(f"📭 Inbox cleared")
    
    # Send summary
    if legit_count + spam_count > 0:
        asyncio.run(send_telegram_summary(legit_count, spam_count))
    
    print(f"\n🎉 FINAL: ✅ {legit_count} legit, 🗑️ {spam_count} spam")
    logging.info(f"Processed {legit_count} legit, {spam_count} spam")

if __name__ == "__main__":
    main()
