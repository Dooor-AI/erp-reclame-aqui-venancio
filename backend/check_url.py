import json

# Read page 1 HTML
with open('debug_html/page_1_20251120_164602.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find __NEXT_DATA__
start = html.find('id="__NEXT_DATA__"')
json_start = html.find('>', start) + 1
json_end = html.find('</script>', json_start)
data = json.loads(html[json_start:json_end])

# Write to file
with open('url_result.txt', 'w', encoding='utf-8') as out:
    complaints = data.get('props', {}).get('pageProps', {}).get('complaintList', {}).get('data', [])
    if complaints:
        c = complaints[0]
        out.write(f"URL field: {c.get('url')}\n")
        out.write(f"ID: {c.get('id')}\n")
        out.write(f"Title: {c.get('title')[:50]}\n")

        # Show what URL we're building
        company_slug = 'drogaria-venancio-site-e-televendas'
        url_path = c.get('url', '').lstrip('/')
        built_url = f"https://www.reclameaqui.com.br/{company_slug}/{url_path}/"
        out.write(f"\nBuilt URL: {built_url}\n")

        # Correct URL should be without doubling the slug
        correct_url = f"https://www.reclameaqui.com.br/{url_path}/"
        out.write(f"Correct URL: {correct_url}\n")
