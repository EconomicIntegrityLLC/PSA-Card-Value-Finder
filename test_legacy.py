import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 Chrome/121.0.0.0'}

# The legacy tool is at 130point.com/legacy/
# Let's check its structure

url = 'https://130point.com/legacy/'
response = requests.get(url, headers=headers)
print(f"Legacy page: {response.status_code}")

soup = BeautifulSoup(response.text, 'lxml')

# Find all forms
forms = soup.find_all('form')
print(f"Forms found: {len(forms)}")

for form in forms:
    action = form.get('action', '')
    method = form.get('method', 'get')
    print(f"\nForm: {action} ({method})")
    inputs = form.find_all('input')
    for inp in inputs:
        name = inp.get('name', '')
        typ = inp.get('type', 'text')
        if name:
            print(f"  - {name} ({typ})")
    selects = form.find_all('select')
    for sel in selects:
        name = sel.get('name', '')
        print(f"  - {name} (select)")

# Look for iframes (they might embed the search)
iframes = soup.find_all('iframe')
print(f"\nIframes found: {len(iframes)}")
for iframe in iframes:
    src = iframe.get('src', '')
    print(f"  {src[:100]}")
