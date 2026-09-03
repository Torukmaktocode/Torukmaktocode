import requests

r = requests.get('https://github-contributions-api.jogruber.de/v4/Torukmaktocode')
data = r.json()
contributions = data['contributions']

total = sum(c['count'] for c in contributions)
print(f'Total contributions: {total}')
print()
print('Dates with contributions:')
for c in contributions:
    if c['count'] > 0:
        print(f'  {c["date"]}: {c["count"]}')
