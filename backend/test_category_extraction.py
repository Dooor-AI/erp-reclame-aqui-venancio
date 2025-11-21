"""Test category extraction from saved HTML"""
from bs4 import BeautifulSoup

# Read one of the saved HTML files
html_file = 'debug_html/page_1_20251117_185246.html'

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Try to find category using new selector
category_elem = soup.find('a', {'id': 'info_segmento_hero'})

if category_elem:
    category_p = category_elem.find('p')
    if category_p:
        category = category_p.get_text(strip=True)
        print(f"✅ Categoria encontrada: {category}")
    else:
        print("❌ Tag <p> não encontrada dentro do link")
else:
    print("❌ Elemento 'info_segmento_hero' não encontrado")

# Also try to find complaint cards
complaint_cards = soup.find_all('div', class_=lambda x: x and 'complaint' in x.lower())
print(f"\nEncontrados {len(complaint_cards)} elementos com 'complaint' no class")
