"""
Scraper using Next.js _next/data endpoint for pagination
Next.js pre-fetches data through this endpoint for client-side navigation
"""
import time
import json
import logging
import re
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.core.database import SessionLocal
from app.db.crud import create_complaint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

COMPANY_SLUG = "drogaria-venancio-site-e-televendas"
BASE_URL = f"https://www.reclameaqui.com.br/empresa/{COMPANY_SLUG}/lista-reclamacoes/"
MAX_PAGES = 30


def get_driver():
    """Setup Chrome"""
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    # Keep visible for debugging
    # options.add_argument('--window-position=-2400,-2400')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')

    driver = uc.Chrome(options=options)
    return driver


def extract_build_id(driver):
    """Extract Next.js build ID from page"""
    try:
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        return data.get("buildId")
    except:
        return None


def extract_complaints_from_json(data):
    """Extract complaints from Next.js JSON data"""
    try:
        page_props = data.get("pageProps", {})
        complaints_data = page_props.get("complaintsData", {}).get("complaints", {})

        if isinstance(complaints_data, dict):
            return complaints_data.get("data", [])
        return complaints_data
    except Exception as e:
        logger.error(f"Error extracting: {e}")
        return []


def parse_complaint(item):
    """Parse complaint data"""
    try:
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
            "url": f"https://www.reclameaqui.com.br/{item.get('id', '')}",
        }
    except Exception as e:
        logger.error(f"Error parsing: {e}")
        return None


def scrape():
    """Main scraping function using Next.js data endpoint"""
    driver = get_driver()
    db = SessionLocal()
    all_complaints = []
    seen_ids = set()

    try:
        # Load first page to get build ID
        logger.info("Loading first page...")
        driver.get(BASE_URL)

        # Wait for Cloudflare
        time.sleep(8)

        # Get build ID
        build_id = extract_build_id(driver)
        logger.info(f"Build ID: {build_id}")

        if not build_id:
            logger.error("Could not get build ID")
            return []

        # Extract first page complaints from __NEXT_DATA__
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        initial_data = json.loads(script_tag.get_attribute("innerHTML"))
        complaints = extract_complaints_from_json(initial_data.get("props", {}))

        for c in complaints:
            cid = c.get("complaintId")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                all_complaints.append(c)

        logger.info(f"Page 1: {len(all_complaints)} complaints")

        # Now fetch remaining pages using _next/data endpoint
        for page in range(2, MAX_PAGES + 1):
            try:
                # Next.js data endpoint format
                # e.g., /_next/data/BUILD_ID/empresa/SLUG/lista-reclamacoes.json?pagina=2
                data_url = f"https://www.reclameaqui.com.br/_next/data/{build_id}/empresa/{COMPANY_SLUG}/lista-reclamacoes.json?pagina={page}"

                logger.info(f"Fetching page {page}: {data_url}")

                # Navigate to data URL directly
                driver.get(data_url)
                time.sleep(2)

                # Get JSON response
                try:
                    # The page content should be JSON
                    body = driver.find_element(By.TAG_NAME, "body")
                    text = body.text

                    # Try to parse as JSON
                    data = json.loads(text)
                    complaints = extract_complaints_from_json(data)

                    new_count = 0
                    for c in complaints:
                        cid = c.get("complaintId")
                        if cid and cid not in seen_ids:
                            seen_ids.add(cid)
                            all_complaints.append(c)
                            new_count += 1

                    logger.info(f"Page {page}: {new_count} new complaints (total: {len(all_complaints)})")

                    if new_count == 0:
                        logger.warning(f"No new complaints on page {page}")

                except json.JSONDecodeError:
                    logger.error(f"Page {page}: Not valid JSON")
                    # Try alternative: navigate to actual page
                    page_url = f"{BASE_URL}?pagina={page}"
                    driver.get(page_url)
                    time.sleep(5)

                    script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
                    page_data = json.loads(script_tag.get_attribute("innerHTML"))
                    complaints = extract_complaints_from_json(page_data.get("props", {}))

                    for c in complaints:
                        cid = c.get("complaintId")
                        if cid and cid not in seen_ids:
                            seen_ids.add(cid)
                            all_complaints.append(c)

            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                continue

            time.sleep(1)

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


if __name__ == "__main__":
    print("=" * 60)
    print("Reclame Aqui Scraper - Next.js Data Endpoint")
    print("=" * 60)

    complaints = scrape()

    print(f"\nTotal complaints collected: {len(complaints)}")
