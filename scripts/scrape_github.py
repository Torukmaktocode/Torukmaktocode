import requests
from datetime import date, timedelta
import json

username = 'Torukmaktocode'

# GitHub's GraphQL API for contribution calendar
query = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            color
          }
        }
      }
    }
  }
}
"""

# We need a token for GraphQL API, but let's try without first
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json',
}

# Try the GraphQL endpoint
url = 'https://api.github.com/graphql'
payload = {
    'query': query,
    'variables': {'username': username}
}

r = requests.post(url, json=payload, headers=headers, timeout=30)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    if 'data' in data:
        cal = data['data']['user']['contributionsCollection']['contributionCalendar']
        print(f"Total contributions: {cal['totalContributions']}")
        
        contributions = {}
        for week in cal['weeks']:
            for day in week['contributionDays']:
                if day['contributionCount'] > 0:
                    contributions[day['date']] = day['contributionCount']
        
        print("\nContributions:")
        for d in sorted(contributions.keys()):
            print(f"  {d}: {contributions[d]}")
    else:
        print(f"Error: {data}")
else:
    print(f"Response: {r.text[:500]}")
