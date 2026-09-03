from datetime import date, timedelta

# Correct contribution data
CORRECT_DATA = {
    "2025-01-09": 2,
    "2025-02-05": 1,
    "2025-07-09": 1,
    "2025-07-16": 1,
    "2025-08-16": 2,
    "2025-08-17": 1,
    "2025-08-22": 3,
    "2026-09-03": 1,
}

today = date.today()
current_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
start_sunday = current_sunday - timedelta(weeks=51)

print(f"Today: {today} ({today.strftime('%A')})")
print(f"Start Sunday: {start_sunday} ({start_sunday.strftime('%A')})")
print(f"Current week starts: {current_sunday}")
print()

print("Contributions and their grid positions:")
for d, count in sorted(CORRECT_DATA.items()):
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
