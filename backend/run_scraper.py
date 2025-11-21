"""
Script to run the Reclame Aqui scraper and import complaints to database
"""
import argparse
import sys
from datetime import datetime
from app.core.database import SessionLocal, init_db
from app.core.config import settings
from app.scraper.reclame_aqui_scraper import ReclameAquiScraper
from app.db.models import Complaint
import logging

# Initialize database tables on startup
init_db()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def import_complaints_to_db(complaints_data: list, db):
    """Import scraped complaints to database"""
    imported = 0
    skipped = 0

    for complaint_data in complaints_data:
        try:
            # Check if complaint already exists (by external_id)
            external_id = complaint_data.get('external_id')
            if external_id:
                existing = db.query(Complaint).filter(
                    Complaint.external_id == external_id
                ).first()
                if existing:
                    logger.debug(f"Complaint {external_id} already exists, skipping")
                    skipped += 1
                    continue

            # Create new complaint
            complaint = Complaint(
                title=complaint_data.get('title', 'Sem título'),
                text=complaint_data.get('text', ''),
                user_name=complaint_data.get('user_name', 'Anônimo'),
                complaint_date=complaint_data.get('complaint_date', datetime.now()),
                status=complaint_data.get('status', 'Não respondida'),
                category=complaint_data.get('category'),  # ✅ FIXED: Now using correct category field
                location=complaint_data.get('location'),  # ✅ ADDED: Location field
                external_id=complaint_data.get('external_id'),
                # Company response from Reclame Aqui
                company_response_text=complaint_data.get('company_response_text'),
                company_response_date=complaint_data.get('company_response_date'),
                customer_evaluation=complaint_data.get('customer_evaluation'),
                evaluation_date=complaint_data.get('evaluation_date'),
                scraped_at=complaint_data.get('scraped_at', datetime.now())
            )

            db.add(complaint)
            db.commit()  # Commit each complaint individually to handle duplicates
            imported += 1
            logger.debug(f"Imported: {complaint.title[:50]}")

        except Exception as e:
            db.rollback()  # Rollback failed insert
            logger.error(f"Error importing complaint: {e}")
            skipped += 1
            continue

    logger.info(f"Successfully imported {imported} complaints, skipped {skipped} duplicates/errors")
    return imported, skipped


def main():
    """Main scraper execution with incremental DB imports"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Reclame Aqui Scraper')
    parser.add_argument('--start-page', type=int, default=1, help='Starting page number')
    parser.add_argument('--max-pages', type=int, default=None, help='Maximum pages to scrape')
    args = parser.parse_args()

    print("=" * 70)
    print("RECLAME AQUI SCRAPER - Collecting Real Complaints")
    print("=" * 70)
    print()

    # Configuration
    company_url = settings.RECLAME_AQUI_COMPANY_URL
    max_pages = args.max_pages or getattr(settings, 'SCRAPER_MAX_PAGES', 3)
    start_page = args.start_page
    delay_min = getattr(settings, 'SCRAPER_DELAY_MIN', 2)
    delay_max = getattr(settings, 'SCRAPER_DELAY_MAX', 5)

    print(f"Company URL: {company_url}")
    print(f"Max pages: {max_pages}")
    print(f"Start page: {start_page}")
    print(f"Delay: {delay_min}-{delay_max} seconds")
    print()

    # Create shared DB session for incremental imports
    db = SessionLocal()
    total_imported = 0
    total_skipped = 0

    def on_page_complete(page_num, complaints_data):
        """Callback called after each page is scraped - imports to DB immediately"""
        nonlocal total_imported, total_skipped

        if not complaints_data:
            return

        imported, skipped = import_complaints_to_db(complaints_data, db)
        total_imported += imported
        total_skipped += skipped

        current_total = db.query(Complaint).count()
        print(f"\n[Page {page_num}] Imported: {imported}, Skipped: {skipped}")
        print(f"[DB Total: {current_total} complaints]\n")

    # Initialize scraper
    # Use fetch_details=True for complete data extraction (slower but includes location)
    # Use page_step=10 to skip pages and avoid duplicates (Reclame Aqui shows overlapping results)
    logger.info("Initializing scraper with full details mode...")
    scraper = ReclameAquiScraper(
        company_url=company_url,
        max_pages=max_pages,
        delay_min=delay_min,
        delay_max=delay_max,
        max_workers=1,  # Sequential processing to avoid DNS errors
        fetch_details=True,  # Fetch individual pages for location and complete data
        start_page=start_page,  # Starting page number
        page_step=1  # Sequential pages for complete data collection
    )

    # Set the callback for incremental imports
    scraper.on_page_complete = on_page_complete

    # Run scraper
    try:
        print("Starting scrape... This may take several minutes.")
        print("Complaints will be imported to DB after each page!")
        print()

        complaints = scraper.scrape_complaints(save_debug=True)

        print()
        print("=" * 70)
        print("SCRAPING RESULTS")
        print("=" * 70)
        print(f"Complaints collected: {len(complaints)}")

        errors = scraper.get_errors()
        if errors:
            print(f"Errors encountered: {len(errors)}")
            print("\nFirst 3 errors:")
            for error in errors[:3]:
                print(f"  - {error}")

        print()

        # Final summary (complaints already imported incrementally)
        print()
        print("=" * 70)
        print("DATABASE IMPORT RESULTS (Incremental)")
        print("=" * 70)
        print(f"Total Imported: {total_imported}")
        print(f"Total Skipped (duplicates): {total_skipped}")
        print(f"Total in database: {db.query(Complaint).count()}")
        print()

        # Show sample
        if total_imported > 0:
            print("Sample of imported complaints:")
            print("-" * 70)
            recent = db.query(Complaint).filter(
                Complaint.external_id != None
            ).order_by(Complaint.scraped_at.desc()).limit(5).all()

            for i, c in enumerate(recent, 1):
                print(f"\n{i}. {c.title}")
                print(f"   Date: {c.complaint_date.strftime('%Y-%m-%d')}")
                print(f"   User: {c.user_name}")
                print(f"   Status: {c.status}")
                print(f"   Preview: {c.text[:100]}...")

        if not complaints and total_imported == 0:
            print("\nNo complaints collected. Possible reasons:")
            print("- Company URL is incorrect")
            print("- Website structure has changed")
            print("- Network/connection issues")
            print("- Check debug_html/ folder for saved pages")

        print()
        print("=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("1. Review scraped complaints in database")
        print("2. Run AI analysis: python validate_analysis.py")
        print("3. Check debug_html/ folder if no complaints found")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n[ERROR] {e}")
        print("\nTroubleshooting:")
        print("- Ensure Chrome/Chromium is installed")
        print("- Check internet connection")
        print("- Verify company URL is correct")
        print("- Check logs for details")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
