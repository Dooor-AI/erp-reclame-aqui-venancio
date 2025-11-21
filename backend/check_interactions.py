"""
Script to check the structure of interactions in individual complaint pages
using Selenium to bypass Cloudflare
"""
import json
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

# URLs to check - use one with ANSWERED status
urls = [
    "https://www.reclameaqui.com.br/drogaria-venancio-site-e-televendas/atraso-na-entrega-e-informacoes-incorretas-sobre-pedido-na-farmacia-venancio-v18_dxtonRxTVnN6QyPt/",
]

# Setup Chrome
options = uc.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-position=-32000,-32000')

driver = uc.Chrome(options=options)

try:
    for url in urls[:1]:  # Just check first one
        print(f"\nFetching: {url}")
        driver.get(url)

        # Wait for page
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Wait for Cloudflare
        time.sleep(5)

        # Parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')

        if script:
            data = json.loads(script.string)
            complaint = data.get('props', {}).get('pageProps', {}).get('complaint', {})

            print(f"\nComplaint title: {complaint.get('title', 'N/A')[:50]}")
            print(f"Status: {complaint.get('status', 'N/A')}")
            print(f"userCity: {complaint.get('userCity', 'N/A')}")
            print(f"userState: {complaint.get('userState', 'N/A')}")

            # Check interactions
            interactions = complaint.get('interactions', [])
            print(f"\nInteractions found: {len(interactions)}")

            if interactions:
                for i, interaction in enumerate(interactions):
                    print(f"\n--- Interaction {i+1} ---")
                    print(f"Type: {interaction.get('type')}")
                    msg = interaction.get('message', '')
                    print(f"Message preview: {msg[:150]}...")
                    print(f"Created: {interaction.get('created')}")
            else:
                print("\nNo interactions array found!")
                print("\nLooking for other possible fields with responses...")

                # Check all keys in complaint
                for key in complaint.keys():
                    if 'reply' in key.lower() or 'response' in key.lower() or 'answer' in key.lower():
                        print(f"  Found: {key} = {str(complaint[key])[:100]}")

            # Save full JSON for inspection
            with open('debug_complaint_json.json', 'w', encoding='utf-8') as f:
                json.dump(complaint, f, indent=2, ensure_ascii=False)
            print("\nFull complaint JSON saved to debug_complaint_json.json")
        else:
            print("No __NEXT_DATA__ script found!")
            # Save HTML for debug
            with open('debug_individual_check.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("HTML saved to debug_individual_check.html")

finally:
    driver.quit()
    print("\nDone!")
