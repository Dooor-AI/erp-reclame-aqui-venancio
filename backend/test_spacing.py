"""
Test different page spacing to find optimal parameter for pagination
"""
import time
import json
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

COMPANY_SLUG = "drogaria-venancio-site-e-televendas"
BASE_URL = f"https://www.reclameaqui.com.br/empresa/{COMPANY_SLUG}/lista-reclamacoes/"

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    return uc.Chrome(options=options)

def test_spacing(driver, spacing, num_pages=18):
    """Test a specific spacing between pages"""
    seen_ids = set()

    # Generate pages with given spacing
    pages = [1] + list(range(1 + spacing, 1 + spacing * num_pages, spacing))[:num_pages-1]

    logger.info(f"\n{'='*50}")
    logger.info(f"Testing spacing={spacing}, pages: {pages[:5]}...{pages[-3:]}")

    for page in pages:
        try:
            url = f"{BASE_URL}?pagina={page}"
            driver.get(url)
            time.sleep(3)

            script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
            data = json.loads(script_tag.get_attribute("innerHTML"))
            page_props = data.get("props", {}).get("pageProps", {})
            complaints = page_props.get("complaints", {}).get("LAST", [])

            new_count = 0
            for c in complaints:
                cid = c.get("complaintId") or c.get("id")
                if cid and cid not in seen_ids:
                    seen_ids.add(cid)
                    new_count += 1

        except Exception as e:
            logger.error(f"Error on page {page}: {e}")
            continue

    total = len(seen_ids)
    efficiency = total / (len(pages) * 10) * 100  # % of max possible

    logger.info(f"Spacing {spacing}: {total} unique complaints from {len(pages)} pages ({efficiency:.1f}% efficiency)")

    return total, efficiency

def main():
    driver = get_driver()

    try:
        # First load to pass Cloudflare
        logger.info("Loading initial page to pass Cloudflare...")
        driver.get(BASE_URL)
        time.sleep(8)

        results = []

        # Test spacing 8, 10, 12, 15
        for spacing in [8, 10, 12, 15]:
            total, efficiency = test_spacing(driver, spacing, num_pages=18)
            results.append((spacing, total, efficiency))

        # Summary
        logger.info(f"\n{'='*50}")
        logger.info("SUMMARY")
        logger.info(f"{'='*50}")
        for spacing, total, efficiency in results:
            logger.info(f"Spacing {spacing}: {total} complaints ({efficiency:.1f}% efficiency)")

        # Best result
        best = max(results, key=lambda x: x[1])
        logger.info(f"\nBest: Spacing {best[0]} with {best[1]} complaints")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
