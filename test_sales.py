import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 Chrome/121.0.0.0'}

# Test their sales search API
# They have a search that returns eBay sold prices

# First check the legacy search page structure
url = 'https://130point.com/legacy/'
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

print("Looking for search forms/endpoints...")

# Check for JavaScript API calls in the page
scripts = soup.find_all('script')
for script in scripts:
    text = script.get_text()
    if 'api' in text.lower() or 'fetch' in text.lower() or 'ajax' in text.lower():
        print(f"Found script with API reference")
        # Print snippet
        if len(text) < 500:
            print(text[:500])

# Try their direct sales search
# Based on URL pattern, try searching for "Jordan PSA 10"
search_url = 'https://130point.com/sales/search.php'
params = {
    'searchterm': 'LeBron James PSA 10 Prizm',
    'sport': 'basketball'
}
response = requests.get(search_url, params=params, headers=headers)
print(f"\nSales search status: {response.status_code}")
print(f"Response length: {len(response.text)}")

if response.status_code == 200 and len(response.text) > 100:
    soup2 = BeautifulSoup(response.text, 'lxml')
    # Look for price data
    tables = soup2.find_all('table')
    print(f"Tables found: {len(tables)}")
    
    # Look for any data elements
    rows = soup2.find_all('tr')
    print(f"Table rows: {len(rows)}")
    if rows:
        for row in rows[:5]:
            cells = row.find_all(['td', 'th'])
            if cells:
                print([c.get_text(strip=True)[:30] for c in cells])
