"""
Scheduler for automated scraping of Reclame Aqui
"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.scraper.reclame_aqui_scraper import ReclameAquiScraper
from app.core.database import SessionLocal
from app.db import crud
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def scrape_job():
    """
    Job that runs periodically to scrape new complaints
    """
    logger.info("=" * 60)
    logger.info("Starting scheduled scraping job")
    logger.info("=" * 60)

    db = None

    try:
        # Initialize scraper
        scraper = ReclameAquiScraper(
            company_url=settings.RECLAME_AQUI_COMPANY_URL,
            max_pages=settings.SCRAPER_MAX_PAGES,
            delay_min=settings.SCRAPER_DELAY_MIN,
            delay_max=settings.SCRAPER_DELAY_MAX
        )

        # Scrape complaints
        logger.info(f"Scraping up to {settings.SCRAPER_MAX_PAGES} pages from {settings.RECLAME_AQUI_COMPANY_URL}")
        complaints = scraper.scrape_complaints(save_debug=False)

        if not complaints:
            logger.warning("No complaints collected in this run")
            return

        logger.info(f"Collected {len(complaints)} complaints from scraper")

        # Save to database
        db = SessionLocal()

        # Filter out duplicates (check by external_id if available)
        new_complaints = []
        duplicate_count = 0

        for complaint in complaints:
            external_id = complaint.get('external_id')

            if external_id:
                # Check if already exists
                existing = crud.get_complaint_by_external_id(db, external_id)
                if existing:
                    duplicate_count += 1
                    continue

            new_complaints.append(complaint)

        if new_complaints:
            count = crud.bulk_create_complaints(db, new_complaints)
            logger.info(f"Saved {count} new complaints to database")
        else:
            logger.info("No new complaints to save (all duplicates)")

        if duplicate_count > 0:
            logger.info(f"Skipped {duplicate_count} duplicate complaints")

        # Report errors
        if scraper.get_errors():
            logger.warning(f"Scraping completed with {len(scraper.get_errors())} errors")
            for error in scraper.get_errors()[:3]:
                logger.warning(f"  - {error}")

    except Exception as e:
        logger.error(f"Error in scraping job: {e}", exc_info=True)

    finally:
        if db:
            db.close()

    logger.info("Scheduled scraping job completed")
    logger.info("=" * 60)


def start_scheduler():
    """
    Start the background scheduler
    """
    interval_hours = settings.SCRAPER_POLLING_INTERVAL_HOURS

    # Add job to scheduler
    scheduler.add_job(
        scrape_job,
        'interval',
        hours=interval_hours,
        id='scrape_complaints',
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )

    # Start scheduler
    scheduler.start()
    logger.info(f"Scheduler started. Will run every {interval_hours} hours.")
    logger.info("First run will occur in {interval_hours} hours, or trigger manually via API")


def stop_scheduler():
    """
    Stop the background scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def run_now():
    """
    Trigger scraping job immediately (for manual triggering)
    """
    logger.info("Manual scraping triggered")
    scrape_job()
