import json
import re

# Read the individual page we saved before
with open('debug_individual.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the script tag with __NEXT_DATA__
start = html.find('id="__NEXT_DATA__"')
if start == -1:
    print("__NEXT_DATA__ not found")
    exit()

# Find the JSON content
json_start = html.find('>', start) + 1
json_end = html.find('</script>', json_start)
json_str = html[json_start:json_end]

data = json.loads(json_str)
complaint = data.get('props', {}).get('pageProps', {}).get('complaint', {})

print('Complaint keys:', list(complaint.keys())[:15])
print()

# Check interactions
interactions = complaint.get('interactions', [])
print(f'Interactions count: {len(interactions)}')

for i, inter in enumerate(interactions):
    print(f'\nInteraction {i+1}:')
    print(f'  Type: {inter.get("type")}')
    msg = inter.get('message', '')
    print(f'  Message preview: {msg[:100]}...' if len(msg) > 100 else f'  Message: {msg}')
