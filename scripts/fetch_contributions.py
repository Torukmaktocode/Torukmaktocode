#!/usr/bin/env python3
"""
Fetch real GitHub contribution data without a token.
Scrapes the public contributions page HTML.
Usage: python fetch_contributions.py [username] [output.json]
"""
import sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def fetch_contributions(username, output_path):
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"📡 Fetching contributions for {username}...")
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Find all day cells
    days = []
    for rect in soup.select("td.ContributionCalendar-day"):
        date_str = rect.get("data-date", "")
        level = rect.get("data-level", "0")
        count_text = rect.get("aria-label", "")
        
        if date_str and level:
            # Extract count from aria-label like "3 contributions on January 1, 2024"
            count = 0
            if "contribution" in count_text:
                try:
                    count = int(count_text.split()[0])
                except (ValueError, IndexError):
                    pass
            
            days.append({
                "date": date_str,
                "level": int(level),
                "count": count
            })
    
    if not days:
        print("❌ No contribution data found. Check username.")
        return
    
    # Calculate stats
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    total = 0
    best_day = {"date": "", "count": 0}
    
    for day in sorted(days, key=lambda x: x["date"]):
        total += day["count"]
        if day["count"] > best_day["count"]:
            best_day = {"date": day["date"], "count": day["count"]}
        if day["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
    
    # Calculate current streak (from today backwards)
    today = datetime.now().date()
    for day in sorted(days, key=lambda x: x["date"], reverse=True):
        d = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if d <= today and day["count"] > 0:
            current_streak += 1
        elif d < today:
            break
    
    # Monthly totals
    monthly = {}
    for day in days:
        month_key = day["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + day["count"]
    
    data = {
        "username": username,
        "fetched_at": datetime.now().isoformat(),
        "days": days,
        "stats": {
            "total_contributions": total,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "best_day": best_day,
            "monthly_totals": monthly
        }
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(days)} days ({total} total contributions)")
    print(f"   Current streak: {current_streak} days")
    print(f"   Longest streak: {longest_streak} days")
    print(f"   Best day: {best_day['date']} ({best_day['count']} contributions)")

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Torukmaktocode"
    output = sys.argv[2] if len(sys.argv) > 2 else "data/contributions.json"
    fetch_contributions(username, output)
