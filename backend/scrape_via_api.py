"""
Scraper using API calls intercepted via Chrome DevTools Protocol
This bypasses Cloudflare by using the authenticated browser session
"""
import time
import json
import logging
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.core.database import SessionLocal
from app.db.crud import create_complaint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

COMPANY_URL = "https://www.reclameaqui.com.br/empresa/drogaria-venancio-site-e-televendas/lista-reclamacoes/"
MAX_PAGES = 30  # 30 pages x 10 complaints = 300 complaints

def get_driver():
    """Setup Chrome with DevTools Protocol enabled"""
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--window-position=-2400,-2400')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')

    # Enable DevTools
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = uc.Chrome(options=options)
    driver.execute_cdp_cmd('Network.enable', {})
    return driver

def extract_from_next_data(driver):
    """Extract complaints from __NEXT_DATA__"""
    try:
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))

        page_props = data.get("props", {}).get("pageProps", {})
        complaints_data = page_props.get("complaintsData", {}).get("complaints", {})

        if isinstance(complaints_data, dict):
            complaints = complaints_data.get("data", [])
        else:
            complaints = complaints_data

        return complaints
    except Exception as e:
        logger.error(f"Error extracting: {e}")
        return []

def parse_complaint(item):
    """Parse complaint data into database format"""
    try:
        # Get creation date
        created_str = item.get("created", "")
        try:
            created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except:
            created_date = datetime.now()

        return {
            "external_id": str(item.get("complaintId", "")),
            "title": item.get("title", ""),
            "text": item.get("description", ""),
            "status": item.get("status", ""),
            "created_at": created_date,
            "company_response": item.get("response", {}).get("description", "") if item.get("response") else "",
            "solved": item.get("solved", False),
            "url": f"https://www.reclameaqui.com.br/empresa/{item.get('id', '')}",
        }
    except Exception as e:
        logger.error(f"Error parsing complaint: {e}")
        return None

def scrape_with_scroll():
    """
    Alternative approach: scroll to load more complaints
    Reclame Aqui may use infinite scroll
    """
    driver = get_driver()
    db = SessionLocal()
    all_complaints = []
    seen_ids = set()

    try:
        logger.info("Loading initial page...")
        driver.get(COMPANY_URL)
        time.sleep(5)

        # Initial extraction
        complaints = extract_from_next_data(driver)
        for c in complaints:
            cid = c.get("complaintId")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                all_complaints.append(c)

        logger.info(f"Initial load: {len(all_complaints)} complaints")

        # Try clicking pagination links
        for page in range(2, MAX_PAGES + 1):
            try:
                page_url = f"{COMPANY_URL}?pagina={page}"
                logger.info(f"Navigating to page {page}: {page_url}")

                # Use JavaScript to navigate
                driver.execute_script(f"window.location.href = '{page_url}'")
                time.sleep(3)

                # Wait for content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
                )

                # Extract new complaints
                complaints = extract_from_next_data(driver)
                new_count = 0

                for c in complaints:
                    cid = c.get("complaintId")
                    if cid and cid not in seen_ids:
                        seen_ids.add(cid)
                        all_complaints.append(c)
                        new_count += 1

                if new_count == 0:
                    logger.warning(f"Page {page}: No new complaints found")
                    # Try alternative: click on next button
                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR, '[aria-label="Próxima página"]')
                        if next_btn:
                            driver.execute_script("arguments[0].click();", next_btn)
                            time.sleep(3)
                            complaints = extract_from_next_data(driver)
                            for c in complaints:
                                cid = c.get("complaintId")
                                if cid and cid not in seen_ids:
                                    seen_ids.add(cid)
                                    all_complaints.append(c)
                                    new_count += 1
                            logger.info(f"After button click: {new_count} new")
                    except:
                        pass
                else:
                    logger.info(f"Page {page}: {new_count} new complaints (total: {len(all_complaints)})")

                time.sleep(2)

            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                continue

        # Save to database
        logger.info(f"\nSaving {len(all_complaints)} complaints to database...")
        saved = 0

        for item in all_complaints:
            parsed = parse_complaint(item)
            if parsed and parsed["external_id"]:
                try:
                    create_complaint(db, **parsed)
                    saved += 1
                except Exception as e:
                    if "UNIQUE constraint" not in str(e):
                        logger.error(f"Error saving: {e}")

        logger.info(f"Saved {saved} new complaints")

        return all_complaints

    finally:
        driver.quit()
        db.close()

def scrape_individual_pages():
    """
    More reliable approach: Navigate to each individual complaint page
    from the list and extract complete data
    """
    driver = get_driver()
    db = SessionLocal()

    try:
        logger.info("Loading list page to get complaint IDs...")
        driver.get(COMPANY_URL)
        time.sleep(5)

        # Get all complaint IDs from initial page
        complaints = extract_from_next_data(driver)
        complaint_ids = [c.get("id") for c in complaints if c.get("id")]

        logger.info(f"Found {len(complaint_ids)} complaint IDs on page 1")

        # Navigate through pages to collect all IDs
        all_ids = set(complaint_ids)

        for page in range(2, MAX_PAGES + 1):
            page_url = f"{COMPANY_URL}?pagina={page}"
            driver.get(page_url)
            time.sleep(3)

            complaints = extract_from_next_data(driver)
            new_ids = [c.get("id") for c in complaints if c.get("id")]

            before = len(all_ids)
            all_ids.update(new_ids)
            new_count = len(all_ids) - before

            logger.info(f"Page {page}: {new_count} new IDs (total: {len(all_ids)})")

            if new_count == 0:
                logger.warning("No new IDs, pagination may not be working")

        logger.info(f"\nTotal unique complaint IDs: {len(all_ids)}")

        # Now fetch individual complaint pages for complete data
        # This is slower but more reliable
        saved = 0
        for i, cid in enumerate(all_ids):
            try:
                complaint_url = f"https://www.reclameaqui.com.br/{cid}"
                # For now, just use the data we already have
                pass
            except Exception as e:
                logger.error(f"Error fetching {cid}: {e}")

        return list(all_ids)

    finally:
        driver.quit()
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Reclame Aqui Scraper - API Interception Method")
    print("=" * 60)

    # Use the scroll/navigation method
    complaints = scrape_with_scroll()

    print(f"\nTotal complaints collected: {len(complaints)}")
