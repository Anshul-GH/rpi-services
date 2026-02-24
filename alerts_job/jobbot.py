#!/usr/bin/env python3
"""
🔥 PRODUCTION JOB BOT - Fully Configurable
"""

import asyncio
import requests
import sqlite3
import time
from datetime import datetime, timedelta
from config import (
    TELEGRAM_TOKEN, CHAT_ID, JOB_CHECK_INTERVAL_HOURS, PRODUCTION_MODE,
    MAX_JOBS_PER_SCAN, BLACKLIST_COMPANIES, MIN_SALARY_K
)
from telegram import Bot

DB_PATH = 'jobs.db'

async def send_message(bot, text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
        return True
    except Exception as e:
        print(f"❌ Send failed: {e}")
        return False

async def get_real_jobs():
    """Production job scraper using your config"""
    url = "https://remoteok.com/api?tags=python"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print("📡 Fetching RemoteOK jobs...")
        resp = requests.get(url, timeout=15, headers=headers)
        print(f"📊 Status: {resp.status_code}")
        
        if resp.status_code != 200:
            return 0
        
        jobs = resp.json()
        senior_keywords = ['senior', 'staff', 'lead', 'principal', 'architect']
        senior_jobs = []
        
        for job in jobs[:MAX_JOBS_PER_SCAN]:
            position = str(job.get('position', '')).lower()
            
            # Senior filter
            if not any(kw in position for kw in senior_keywords):
                continue
                
            # Salary filter
            salary_min = job.get('salary_min', 0)
            if salary_min and salary_min < MIN_SALARY_K:
                continue
                
            # Company blacklist
            company = job.get('company', '').lower()
            if any(bl in company for bl in BLACKLIST_COMPANIES):
                continue
                
            senior_jobs.append(job)
        
        print(f"🎯 {len(senior_jobs)} filtered senior jobs")
        
        conn = sqlite3.connect(DB_PATH)
        bot = Bot(token=TELEGRAM_TOKEN)
        sent = 0
        
        for job in senior_jobs[:5]:
            job_url = job.get('url', f"https://remoteok.com/remote-jobs/{job.get('id')}")
            
            if not conn.execute("SELECT 1 FROM jobs WHERE url=?", (job_url,)).fetchone():
                title = job.get('position', 'N/A')
                company = job.get('company', 'N/A')
                
                conn.execute("INSERT INTO jobs VALUES (?, ?, ?, ?)", 
                           (job_url, title, company, datetime.now().isoformat()))
                
                salary = f"${job.get('salary_min', 'N/A')}k+"
                msg = f"""🚀 <b>NEW {title.upper()}</b>

🏢 <b>{company}</b>
💰 <b>{salary}</b>
📍 Remote

🔗 <a href="{job_url}">Apply Now</a>"""
                
                if await send_message(bot, msg):
                    print(f"✅ SENT: {title}")
                    sent += 1
                time.sleep(0.5)
        
        conn.commit()
        conn.close()
        return sent
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

async def main():
    """Main entrypoint"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS jobs 
                    (url TEXT PRIMARY KEY, title TEXT, company TEXT, posted TEXT)''')
    conn.close()
    
    print(f"🔥 JOB BOT | Interval: {JOB_CHECK_INTERVAL_HOURS}h | Production: {PRODUCTION_MODE}")
    print(f"⏰ Next: {datetime.now() + timedelta(hours=JOB_CHECK_INTERVAL_HOURS)}")
    
    new_jobs = await get_real_jobs()
    print(f"✅ Complete | New: {new_jobs} | Next: +{JOB_CHECK_INTERVAL_HOURS}h")

if __name__ == "__main__":
    asyncio.run(main())
