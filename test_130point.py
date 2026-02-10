import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 Chrome/121.0.0.0'}

# Try the checklists which should have actual set lists
url = 'https://130point.com/checklists/basketball/'
response = requests.get(url, headers=headers)
print(f'Checklists page: {response.status_code}')

soup = BeautifulSoup(response.text, 'lxml')

# Find all links with years (like "2023-24 Prizm")
links = soup.find_all('a', href=True)
sets_found = []
for link in links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    # Look for set names with years
    if re.search(r'\d{4}', text) and 'checklist' in href.lower():
        sets_found.append((text, href))

print(f'\nFound {len(sets_found)} sets with checklists')
for name, href in sets_found[:30]:
    print(f'  {name}: {href}')
