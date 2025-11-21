"""
Script to run the Reclame Aqui scraper with incremental database import
Imports data to DB every 2 pages for real-time consumption in the frontend
"""
import sys
import time
from datetime import datetime
from app.core.database import SessionLocal
from app.core.config import settings
from app.scraper.reclame_aqui_scraper import ReclameAquiScraper
from app.db.models import Complaint
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_incremental.log'),
        logging.StreamHandler()
    ]
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
                category=complaint_data.get('category'),
                location=complaint_data.get('location'),
                external_id=complaint_data.get('external_id'),
                company_response_text=complaint_data.get('company_response_text'),
                company_response_date=complaint_data.get('company_response_date'),
                customer_evaluation=complaint_data.get('customer_evaluation'),
                scraped_at=complaint_data.get('scraped_at', datetime.now())
            )

            db.add(complaint)
            imported += 1
            logger.debug(f"Imported: {complaint.title[:50]}")

        except Exception as e:
            logger.error(f"Error importing complaint: {e}")
            continue

    try:
        db.commit()
        logger.info(f"Successfully imported {imported} complaints, skipped {skipped} duplicates")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing to database: {e}")
        raise

    return imported, skipped


def main():
    """Main scraper execution with incremental import"""
    print("=" * 70)
    print("RECLAME AQUI SCRAPER - INCREMENTAL MODE")
    print("Importing to DB every 2 pages for real-time consumption")
    print("=" * 70)
    print()

    # Configuration
    company_url = settings.RECLAME_AQUI_COMPANY_URL
    max_pages = getattr(settings, 'SCRAPER_MAX_PAGES', 100)
    delay_min = getattr(settings, 'SCRAPER_DELAY_MIN', 2)
    delay_max = getattr(settings, 'SCRAPER_DELAY_MAX', 5)
    pages_per_batch = 2  # Import to DB every 2 pages

    print(f"Company URL: {company_url}")
    print(f"Max pages: {max_pages}")
    print(f"Delay: {delay_min}-{delay_max} seconds")
    print(f"Import frequency: Every {pages_per_batch} pages")
    print()

    total_imported = 0
    total_skipped = 0
    total_errors = 0

    try:
        # Process in batches of 2 pages
        for batch_start in range(1, max_pages + 1, pages_per_batch):
            batch_end = min(batch_start + pages_per_batch - 1, max_pages)
            current_batch = batch_end - batch_start + 1

            print()
            print("=" * 70)
            print(f"BATCH: Pages {batch_start}-{batch_end} ({current_batch} pages)")
            print("=" * 70)
            print()

            # Initialize scraper for this batch
            logger.info(f"Initializing scraper for pages {batch_start}-{batch_end}...")
            scraper = ReclameAquiScraper(
                company_url=company_url,
                max_pages=current_batch,
                delay_min=delay_min,
                delay_max=delay_max,
                max_workers=4,  # Optimized to 4 workers to avoid rate limiting
                start_page=batch_start  # Start from specific page
            )

            # Run scraper for this batch
            print(f"Scraping pages {batch_start}-{batch_end}...")
            start_time = time.time()

            complaints = scraper.scrape_complaints(save_debug=False)

            elapsed = time.time() - start_time
            errors = scraper.get_errors()

            print()
            print(f"Batch completed in {elapsed:.1f} seconds")
            print(f"Complaints collected: {len(complaints)}")
            print(f"Errors: {len(errors)}")

            # Import to database immediately
            if complaints:
                print()
                print(f"Importing {len(complaints)} complaints to database...")
                db = SessionLocal()
                try:
                    imported, skipped = import_complaints_to_db(complaints, db)
                    total_imported += imported
                    total_skipped += skipped

                    total_in_db = db.query(Complaint).count()

                    print(f"Imported: {imported}")
                    print(f"Skipped (duplicates): {skipped}")
                    print(f"Total in database: {total_in_db}")

                finally:
                    db.close()

            total_errors += len(errors)

            # Progress summary
            print()
            print("-" * 70)
            print("OVERALL PROGRESS")
            print("-" * 70)
            print(f"Pages processed: {batch_end}/{max_pages}")
            print(f"Total imported: {total_imported}")
            print(f"Total skipped: {total_skipped}")
            print(f"Total errors: {total_errors}")
            progress = (batch_end / max_pages) * 100
            print(f"Progress: {progress:.1f}%")
            print("-" * 70)

            # Small delay between batches
            if batch_end < max_pages:
                print()
                print("Waiting 5 seconds before next batch...")
                time.sleep(5)

        # Final summary
        print()
        print("=" * 70)
        print("SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Total pages processed: {max_pages}")
        print(f"Total imported: {total_imported}")
        print(f"Total skipped (duplicates): {total_skipped}")
        print(f"Total errors: {total_errors}")

        db = SessionLocal()
        try:
            total_in_db = db.query(Complaint).count()
            print(f"Total complaints in database: {total_in_db}")
        finally:
            db.close()

        print("=" * 70)

    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("SCRAPING INTERRUPTED BY USER")
        print("=" * 70)
        print(f"Imported so far: {total_imported}")
        print(f"Skipped so far: {total_skipped}")
        print(f"Errors so far: {total_errors}")
        print("=" * 70)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n[ERROR] {e}")
        print("\nTroubleshooting:")
        print("- Ensure Chrome/Chromium is installed")
        print("- Check internet connection")
        print("- Verify company URL is correct")
        print("- Check logs for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
