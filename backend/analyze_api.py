"""Script to analyze Reclame Aqui API structure from saved HTML"""
import re
import json

# Read the HTML file
with open('debug_html/page_1_20251121_080756.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find API URLs
api_urls = re.findall(r'https?://[^\"\s<>]+(?:api\.reclameaqui|graphql)[^\"\s<>]*', html)
print("=== API URLs Found ===")
for url in set(api_urls):
    print(url)

# Find qlEndpoint references
ql_refs = re.findall(r'qlEndpoint[^,}]+', html)
print("\n=== qlEndpoint References ===")
for ref in set(ql_refs):
    print(ref[:200])

# Look for query patterns
queries = re.findall(r'query[A-Za-z]+|mutation[A-Za-z]+', html)
print("\n=== GraphQL Query Names ===")
for q in set(queries):
    print(q)

# Extract __NEXT_DATA__ to analyze structure
next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
if next_data_match:
    try:
        data = json.loads(next_data_match.group(1))

        # Look for API configuration
        print("\n=== Next.js Runtime Config ===")
        if 'runtimeConfig' in data:
            print(json.dumps(data['runtimeConfig'], indent=2)[:500])

        # Look at buildId for potential API versioning
        if 'buildId' in data:
            print(f"\nBuild ID: {data['buildId']}")

        # Check for queries in props
        print("\n=== Props Structure Keys ===")
        if 'props' in data and 'pageProps' in data['props']:
            page_props = data['props']['pageProps']
            for key in page_props.keys():
                print(f"  - {key}")

            # Analyze complaints structure
            if 'complaints' in page_props:
                complaints = page_props['complaints']
                print(f"\n=== Complaints Structure ===")
                print(f"Type: {type(complaints)}")
                if isinstance(complaints, dict):
                    for key in complaints.keys():
                        print(f"  - {key}")
                    if 'complaintsData' in complaints:
                        print(f"\nNumber of complaints: {len(complaints['complaintsData'])}")
                        if complaints['complaintsData']:
                            print(f"\nFirst complaint keys: {list(complaints['complaintsData'][0].keys())}")
                    if 'totalComplaintsCount' in complaints:
                        print(f"Total count: {complaints['totalComplaintsCount']}")

            # Analyze company structure to get company ID
            if 'company' in page_props:
                company = page_props['company']
                print(f"\n=== Company Info ===")
                if isinstance(company, dict):
                    if 'id' in company:
                        print(f"Company ID: {company['id']}")
                    if 'shortname' in company:
                        print(f"Shortname: {company['shortname']}")
                    if 'companyId' in company:
                        print(f"CompanyId: {company['companyId']}")

    except json.JSONDecodeError as e:
        print(f"Error parsing __NEXT_DATA__: {e}")
