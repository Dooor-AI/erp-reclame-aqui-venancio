"""Debug script to check URL field format in JSON"""
import json
from bs4 import BeautifulSoup

# Read the saved page HTML
with open('debug_html/page_1_20251120_164602.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')

if script:
    data = json.loads(script.string)
    complaints = data.get('props', {}).get('pageProps', {}).get('complaints', {}).get('LAST', [])

    print(f"Found {len(complaints)} complaints")
    print("\nFirst 3 URL fields:")
    for i, c in enumerate(complaints[:3]):
        url = c.get('url', 'NO URL')
        title = c.get('title', 'NO TITLE')[:50]
        print(f"\n{i+1}. Title: {title}...")
        print(f"   URL field: {url}")
        print(f"   Full URL should be: https://www.reclameaqui.com.br/{url}/")
