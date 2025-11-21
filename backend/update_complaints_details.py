"""
Script to update existing complaints with detailed information
Fetches individual complaint pages to get:
- Complete status (Resolvida, Não Resolvida, etc.)
- Company response
- Customer evaluation
"""
import time
import json
import logging
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from app.core.database import SessionLocal
from app.db.models import Complaint
import re
import unicodedata

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def slugify(text):
    """Convert text to URL slug"""
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and replace spaces/special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text[:80]  # Limit length

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    return uc.Chrome(options=options)

def extract_complaint_details(driver, external_id, title):
    """Extract detailed info from individual complaint page"""
    # Build URL with slug from title: slug_ID
    slug = slugify(title)
    url = f"https://www.reclameaqui.com.br/drogaria-venancio-site-e-televendas/{slug}_{external_id}/"

    try:
        driver.get(url)
        time.sleep(3)

        # Get page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        details = {
            'status': None,
            'company_response_text': None,
            'company_response_date': None,
            'customer_evaluation': None,
            'evaluation_date': None,
            'location': None
        }

        # Extract status from __NEXT_DATA__
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        if script_tag:
            try:
                data = json.loads(script_tag.string)
                # Try 'complaint' key first, then 'complaintDetail'
                page_props = data.get('props', {}).get('pageProps', {})
                complaint_data = page_props.get('complaint') or page_props.get('complaintDetail', {})

                # Status mapping
                status_map = {
                    'PENDING': 'Não respondida',
                    'ANSWERED': 'Respondida',
                    'SOLVED': 'Resolvida',
                    'UNSOLVED': 'Não resolvida',
                    'IN_REPLICA': 'Em réplica',
                    'EVALUATED': 'Avaliada',
                    'FROZEN': 'Congelada'
                }

                raw_status = complaint_data.get('status', '')
                details['status'] = status_map.get(raw_status, raw_status)

                # Check for evaluation
                evaluated = complaint_data.get('evaluated', False)
                deal_again = complaint_data.get('dealAgain')

                if evaluated:
                    if deal_again == True:
                        details['status'] = 'Resolvida'
                    elif deal_again == False:
                        details['status'] = 'Não resolvida'

                # Location
                details['location'] = complaint_data.get('userCity', '')
                if complaint_data.get('userState'):
                    if details['location']:
                        details['location'] += f" - {complaint_data.get('userState')}"
                    else:
                        details['location'] = complaint_data.get('userState')

                # Company response
                interactions = complaint_data.get('interactions', [])
                for interaction in interactions:
                    if interaction.get('type') == 'COMPANY':
                        details['company_response_text'] = interaction.get('message', '')
                        created = interaction.get('created', '')
                        if created:
                            try:
                                details['company_response_date'] = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            except:
                                pass
                        break

                # Customer evaluation
                for interaction in interactions:
                    if interaction.get('type') == 'CONSUMER_FINAL':
                        details['customer_evaluation'] = interaction.get('message', '')
                        created = interaction.get('created', '')
                        if created:
                            try:
                                details['evaluation_date'] = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            except:
                                pass
                        break

            except Exception as e:
                logger.error(f"Error parsing JSON: {e}")

        return details

    except Exception as e:
        logger.error(f"Error fetching {external_id}: {e}")
        return None

def process_complaint(complaint_data):
    """Process a single complaint - used by workers"""
    complaint_id, external_id, title = complaint_data
    driver = None
    try:
        driver = get_driver()
        details = extract_complaint_details(driver, external_id, title)
        return (complaint_id, details)
    except Exception as e:
        logger.error(f"Worker error for {external_id}: {e}")
        return (complaint_id, None)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def update_complaints():
    """Update all complaints with detailed information using 2 workers"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    db = SessionLocal()

    try:
        # Get complaints that need updating
        complaints = db.query(Complaint).filter(
            Complaint.external_id.isnot(None)
        ).all()

        total = len(complaints)
        logger.info(f"Found {total} complaints to update with 2 workers")

        # Prepare complaint data for workers
        complaint_data = [(c.id, c.external_id, c.title) for c in complaints]

        updated = 0
        errors = 0
        completed = 0
        lock = threading.Lock()

        def update_db(complaint_id, details):
            nonlocal updated, errors, completed
            db_local = SessionLocal()
            try:
                complaint = db_local.query(Complaint).filter(Complaint.id == complaint_id).first()
                if complaint and details:
                    if details['status']:
                        complaint.status = details['status']
                    if details['company_response_text']:
                        complaint.company_response_text = details['company_response_text']
                    if details['company_response_date']:
                        complaint.company_response_date = details['company_response_date']
                    if details['customer_evaluation']:
                        complaint.customer_evaluation = details['customer_evaluation']
                    if details['evaluation_date']:
                        complaint.evaluation_date = details['evaluation_date']
                    if details['location']:
                        complaint.location = details['location']
                    db_local.commit()
                    with lock:
                        updated += 1
                        completed += 1
                        logger.info(f"[{completed}/{total}] {complaint.external_id}: {details['status']}")
                else:
                    with lock:
                        errors += 1
                        completed += 1
            finally:
                db_local.close()

        # Process with 2 workers
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(process_complaint, data): data for data in complaint_data}

            for future in as_completed(futures):
                complaint_id, details = future.result()
                update_db(complaint_id, details)

        logger.info(f"\nCompleted! Updated: {updated}, Errors: {errors}")

        # Show status distribution
        from sqlalchemy import distinct
        for status in db.query(distinct(Complaint.status)).all():
            count = db.query(Complaint).filter(Complaint.status == status[0]).count()
            logger.info(f"  {status[0]}: {count}")

    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Update Complaints with Detailed Information")
    print("=" * 60)
    print("\nThis will fetch each complaint page to get:")
    print("- Complete status (Resolvida, Não Resolvida, etc.)")
    print("- Company response text and date")
    print("- Customer evaluation")
    print("- Location")
    print("\nEstimated time: ~3 seconds per complaint")
    print("=" * 60)

    update_complaints()
