"""
Test different tabs/filters for Reclame Aqui
Check if we can get more complaints through different tabs
"""
import time
import json
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

COMPANY_SLUG = "drogaria-venancio-site-e-televendas"

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    return uc.Chrome(options=options)

def test_tabs():
    driver = get_driver()

    try:
        # Load page and get build ID
        logger.info("Loading page...")
        driver.get(f"https://www.reclameaqui.com.br/empresa/{COMPANY_SLUG}/lista-reclamacoes/")
        time.sleep(8)

        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        build_id = data.get("buildId")

        # Check available tabs/filters
        page_props = data.get("props", {}).get("pageProps", {})
        complaints = page_props.get("complaints", {})

        logger.info(f"\n=== Available data ===")
        logger.info(f"Tab: {complaints.get('tab')}")
        logger.info(f"Total count: {complaints.get('count')}")
        logger.info(f"Categories: {len(complaints.get('categories', []))}")
        logger.info(f"Problems: {len(complaints.get('problems', []))}")
        logger.info(f"Products: {len(complaints.get('products', []))}")

        # Try different URL patterns to see if we can get more data
        test_urls = [
            # Different tabs
            f"?tab=LAST",
            f"?tab=SOLVED",
            f"?tab=NOT_SOLVED",
            f"?tab=EVALUATED",
            f"?status=SOLVED",
            f"?status=NOT_SOLVED",
            # Try older pages
            f"?pagina=10",
            f"?pagina=50",
            f"?pagina=100",
        ]

        base_url = f"https://www.reclameaqui.com.br/empresa/{COMPANY_SLUG}/lista-reclamacoes/"

        seen_ids = set()

        for params in test_urls:
            url = f"{base_url}{params}"
            logger.info(f"\nTesting: {params}")

            driver.get(url)
            time.sleep(4)

            try:
                script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
                data = json.loads(script_tag.get_attribute("innerHTML"))
                page_props = data.get("props", {}).get("pageProps", {})
                complaints_data = page_props.get("complaints", {})

                complaints = complaints_data.get("LAST", [])
                tab = complaints_data.get("tab", "?")
                count = complaints_data.get("count", 0)

                new_count = 0
                for c in complaints:
                    cid = c.get("complaintId") or c.get("id")
                    if cid and cid not in seen_ids:
                        seen_ids.add(cid)
                        new_count += 1

                logger.info(f"  Tab: {tab}, Count: {count}, Got: {len(complaints)}, New: {new_count}")

                if complaints:
                    logger.info(f"  First ID: {complaints[0].get('id')}")

            except Exception as e:
                logger.error(f"  Error: {e}")

        logger.info(f"\n\nTotal unique complaints: {len(seen_ids)}")

        # Now let's test scrolling behavior - maybe it loads more via client-side
        logger.info("\n\n=== Testing scroll loading ===")
        driver.get(f"{base_url}")
        time.sleep(5)

        # Check initial count
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        initial = data.get("props", {}).get("pageProps", {}).get("complaints", {}).get("LAST", [])
        logger.info(f"Initial complaints: {len(initial)}")

        # Scroll down multiple times
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Check if new complaints were loaded
        # They might be in the DOM but not in __NEXT_DATA__
        cards = driver.find_elements(By.CSS_SELECTOR, '[class*="ComplaintCard"]')
        links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="reclameaqui.com.br/"][href*="venancio"]')

        logger.info(f"Cards found after scroll: {len(cards)}")
        logger.info(f"Complaint links found: {len(links)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_tabs()
