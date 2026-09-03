import requests
from datetime import date, timedelta

r = requests.get('https://github-contributions-api.jogruber.de/v4/Torukmaktocode')
data = r.json()['contributions']
today = date.today()

print(f"Today: {today} ({today.strftime('%A')})")
print()

# Find contributions with data
active = [(c['date'], c['count']) for c in data if c['count'] > 0]
active.sort()

print("All contributions:")
for d, count in active:
    dt = date.fromisoformat(d)
    print(f"  {d} ({dt.strftime('%A')}): {count}")

print()
print(f"Total: {sum(c for _, c in active)}")
