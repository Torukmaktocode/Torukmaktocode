import requests
from datetime import date, timedelta

r = requests.get('https://github-contributions-api.jogruber.de/v4/Torukmaktocode')
data = r.json()['contributions']
days = {c['date']: c['count'] for c in data}
today = date.today()

# Calculate the same way as the heatmap
current_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
start_sunday = current_sunday - timedelta(weeks=51)

print(f"Today: {today} ({today.strftime('%A')})")
print(f"Start Sunday: {start_sunday} ({start_sunday.strftime('%A')})")
print(f"Current week starts: {current_sunday}")
print()

# Check each contribution's position
contributions = [(c['date'], c['count']) for c in data if c['count'] > 0]
contributions.sort()

print("Contributions and their grid positions:")
for d, count in contributions:
    dt = date.fromisoformat(d)
    if dt < start_sunday:
        print(f"  {d} ({dt.strftime('%A')}): {count} - BEFORE RANGE")
        continue
    if dt > today:
        print(f"  {d} ({dt.strftime('%A')}): {count} - AFTER TODAY")
        continue
    
    weeks_diff = (dt - start_sunday).days // 7
    day_of_week = dt.weekday()  # 0=Mon, 6=Sun
    
    # Convert to our grid: 0=Sun, 1=Mon, ..., 6=Sat
    grid_day = (day_of_week + 1) % 7
    
    print(f"  {d} ({dt.strftime('%A')}): {count} -> week {weeks_diff}, day {grid_day}")
