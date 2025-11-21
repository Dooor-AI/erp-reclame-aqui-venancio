import requests
import json

response = requests.get("http://localhost:8000/openapi.json")
data = response.json()

print("=== All Analytics Routes ===")
for path in sorted(data['paths'].keys()):
    if 'analytics' in path:
        print(f"  {path}")

print("\n=== All Available Routes ===")
for path in sorted(data['paths'].keys()):
    print(f"  {path}")
