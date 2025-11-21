"""
Test different pagination approaches for Reclame Aqui
The goal is to find if there's a way to get more than 10 complaints
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

def test_pagination():
    driver = get_driver()

    try:
        # First, load the page to get build ID
        logger.info("Loading initial page to get build ID...")
        driver.get(f"https://www.reclameaqui.com.br/empresa/{COMPANY_SLUG}/lista-reclamacoes/")
        time.sleep(8)

        # Get build ID
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        build_id = data.get("buildId")
        logger.info(f"Build ID: {build_id}")

        # Analyze the structure of complaints
        page_props = data.get("props", {}).get("pageProps", {})

        logger.info("\n=== pageProps keys ===")
        for key in page_props.keys():
            logger.info(f"  - {key}")

        # Check complaints structure
        if "complaints" in page_props:
            complaints = page_props["complaints"]
            logger.info(f"\n=== complaints type: {type(complaints)} ===")
            if isinstance(complaints, dict):
                for key in complaints.keys():
                    val = complaints[key]
                    if isinstance(val, list):
                        logger.info(f"  - {key}: list with {len(val)} items")
                    elif isinstance(val, dict):
                        logger.info(f"  - {key}: dict with keys {list(val.keys())[:5]}")
                    else:
                        logger.info(f"  - {key}: {type(val).__name__} = {str(val)[:100]}")

        # Also check complaintsData if exists
        if "complaintsData" in page_props:
            complaints_data = page_props["complaintsData"]
            logger.info(f"\n=== complaintsData ===")
            if isinstance(complaints_data, dict):
                for key in complaints_data.keys():
                    logger.info(f"  - {key}")

        # Now test different pagination URLs
        logger.info("\n\n=== Testing pagination URLs ===")

        test_urls = [
            # Standard ?pagina= parameter
            f"/_next/data/{build_id}/empresa/{COMPANY_SLUG}/lista-reclamacoes.json?pagina=2",
            f"/_next/data/{build_id}/empresa/{COMPANY_SLUG}/lista-reclamacoes.json?pagina=3",
            # Try offset/limit style
            f"/_next/data/{build_id}/empresa/{COMPANY_SLUG}/lista-reclamacoes.json?offset=10&limit=10",
            f"/_next/data/{build_id}/empresa/{COMPANY_SLUG}/lista-reclamacoes.json?page=2",
            # Try index parameter
            f"/_next/data/{build_id}/empresa/{COMPANY_SLUG}/lista-reclamacoes.json?index=10",
        ]

        seen_ids = set()

        for url in test_urls:
            full_url = f"https://www.reclameaqui.com.br{url}"
            logger.info(f"\nTesting: {url.split('.json')[1]}")

            driver.get(full_url)
            time.sleep(2)

            try:
                body = driver.find_element(By.TAG_NAME, "body")
                text = body.text
                data = json.loads(text)

                # Try multiple paths
                complaints = []
                page_props = data.get("pageProps", {})

                # Path 1: pageProps.complaints.LAST
                if "complaints" in page_props:
                    c = page_props["complaints"]
                    if isinstance(c, dict) and "LAST" in c:
                        complaints = c["LAST"]
                        logger.info(f"  Found in complaints.LAST: {len(complaints)} items")

                # Path 2: pageProps.complaintsData.complaints.data
                if not complaints and "complaintsData" in page_props:
                    cd = page_props["complaintsData"]
                    if isinstance(cd, dict) and "complaints" in cd:
                        cc = cd["complaints"]
                        if isinstance(cc, dict) and "data" in cc:
                            complaints = cc["data"]
                            logger.info(f"  Found in complaintsData.complaints.data: {len(complaints)} items")

                # Check for new complaints
                new_count = 0
                for c in complaints:
                    cid = c.get("complaintId") or c.get("id")
                    if cid and cid not in seen_ids:
                        seen_ids.add(cid)
                        new_count += 1

                logger.info(f"  New complaints: {new_count}, Total unique: {len(seen_ids)}")

                if complaints:
                    logger.info(f"  First ID: {complaints[0].get('complaintId') or complaints[0].get('id')}")

            except json.JSONDecodeError:
                logger.error(f"  Not valid JSON")
            except Exception as e:
                logger.error(f"  Error: {e}")

        # Final test: Navigate to actual pages to see if HTML version paginates
        logger.info("\n\n=== Testing HTML page navigation ===")

        for page_num in [1, 2, 3]:
            url = f"https://www.reclameaqui.com.br/empresa/{COMPANY_SLUG}/lista-reclamacoes/?pagina={page_num}"
            logger.info(f"\nPage {page_num}: {url}")

            driver.get(url)
            time.sleep(5)

            script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
            data = json.loads(script_tag.get_attribute("innerHTML"))
            page_props = data.get("props", {}).get("pageProps", {})

            complaints = []
            if "complaints" in page_props:
                c = page_props["complaints"]
                if isinstance(c, dict) and "LAST" in c:
                    complaints = c["LAST"]

            if complaints:
                ids = [str(c.get("complaintId") or c.get("id")) for c in complaints[:3]]
                logger.info(f"  Got {len(complaints)} complaints, first IDs: {ids}")

        logger.info(f"\n\nTotal unique complaints found: {len(seen_ids)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_pagination()
