"""
Scraper that properly paginates through Reclame Aqui pages
Uses wide spread of page numbers to avoid ISR cache overlap
"""
import time
import json
import logging
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from app.core.database import SessionLocal
from app.db.models import Complaint
from app.schemas.complaint import ComplaintCreate

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

def parse_complaint(item):
    """Parse complaint to database format"""
    try:
        created_str = item.get("created", "")
        try:
            created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except:
            created_date = datetime.now()

        external_id = item.get("complaintId") or item.get("id") or ""
        return {
            "external_id": str(external_id),
            "title": item.get("title", ""),
            "text": item.get("description", ""),
            "status": item.get("status", ""),
            "complaint_date": created_date,
        }
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return None

def scrape():
    """Scrape with proper pagination"""
    driver = get_driver()
    db = SessionLocal()
    all_complaints = []
    seen_ids = set()

    try:
        # First page
        logger.info("Loading first page...")
        driver.get(BASE_URL)
        time.sleep(8)

        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        page_props = data.get("props", {}).get("pageProps", {})
        complaints_data = page_props.get("complaints", {})

        # Get total count
        total_count = complaints_data.get("count", 0)
        logger.info(f"Total complaints available: {total_count}")

        # Extract first page
        complaints = complaints_data.get("LAST", [])
        for c in complaints:
            cid = c.get("complaintId") or c.get("id")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                all_complaints.append(c)

        logger.info(f"Page 1: {len(complaints)} complaints, {len(all_complaints)} unique")

        # Calculate pages to visit (spread out to avoid cache overlap)
        # Each page has ~10 items, so for 300 complaints we need ~30 pages
        # But pages have overlap, so we'll visit more and spread them out
        max_pages = min(1200, total_count // 10)  # ~1200 pages available

        # Generate list of pages to visit - spread evenly
        # Visit every 10th page (99.4% efficiency based on testing)
        pages_to_visit = list(range(11, min(max_pages, 320), 10))  # Pages 11, 21, 31...

        logger.info(f"Will visit {len(pages_to_visit)} pages")

        for i, page in enumerate(pages_to_visit):
            try:
                url = f"{BASE_URL}?pagina={page}"
                logger.info(f"Page {page} ({i+1}/{len(pages_to_visit)})...")

                driver.get(url)
                time.sleep(4)

                script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
                data = json.loads(script_tag.get_attribute("innerHTML"))
                page_props = data.get("props", {}).get("pageProps", {})
                complaints = page_props.get("complaints", {}).get("LAST", [])

                new_count = 0
                for c in complaints:
                    cid = c.get("complaintId") or c.get("id")
                    if cid and cid not in seen_ids:
                        seen_ids.add(cid)
                        all_complaints.append(c)
                        new_count += 1

                logger.info(f"  Got {len(complaints)}, {new_count} new (total: {len(all_complaints)})")

                # Stop if we have enough
                if len(all_complaints) >= 300:
                    logger.info("Reached 300+ complaints, stopping")
                    break

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
                    # Check if already exists
                    existing = db.query(Complaint).filter(Complaint.external_id == parsed["external_id"]).first()
                    if not existing:
                        db_complaint = Complaint(**parsed)
                        db.add(db_complaint)
                        db.commit()
                        saved += 1
                except Exception as e:
                    db.rollback()
                    if "UNIQUE constraint" not in str(e):
                        logger.error(f"Save error: {e}")

        logger.info(f"Saved {saved} new complaints")
        return all_complaints

    finally:
        driver.quit()
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Reclame Aqui Scraper - Paginated")
    print("=" * 60)

    complaints = scrape()
    print(f"\nTotal complaints collected: {len(complaints)}")
