"""
Test script for Reclame Aqui scraper
Run this to test the scraper independently before integrating with the API
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.scraper.reclame_aqui_scraper import ReclameAquiScraper
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Test the scraper"""
    logger.info("=" * 60)
    logger.info("Testing Reclame Aqui Scraper")
    logger.info("=" * 60)

    # Initialize scraper - start with just 2 pages for testing
    scraper = ReclameAquiScraper(
        company_url=settings.RECLAME_AQUI_COMPANY_URL,
        max_pages=2,  # Test with 2 pages first
        delay_min=settings.SCRAPER_DELAY_MIN,
        delay_max=settings.SCRAPER_DELAY_MAX
    )

    # Run scraper
    logger.info(f"Scraping {settings.RECLAME_AQUI_COMPANY_URL}")
    complaints = scraper.scrape_complaints(save_debug=True)

    # Report results
    logger.info("=" * 60)
    logger.info(f"Scraping Results")
    logger.info("=" * 60)
    logger.info(f"Total complaints collected: {len(complaints)}")

    if scraper.get_errors():
        logger.warning(f"Errors encountered: {len(scraper.get_errors())}")
        for error in scraper.get_errors()[:5]:  # Show first 5 errors
            logger.warning(f"  - {error}")

    if complaints:
        logger.info("\nFirst complaint:")
        first = complaints[0]
        for key, value in first.items():
            if key != 'text':  # Don't print full text
                logger.info(f"  {key}: {value}")
        logger.info(f"  text: {first.get('text', '')[:100]}...")

        logger.info("\nSample of collected complaints:")
        for i, complaint in enumerate(complaints[:5], 1):
            logger.info(f"{i}. {complaint.get('title', 'N/A')[:60]} - {complaint.get('user_name', 'N/A')}")

    else:
        logger.error("No complaints were collected!")
        logger.error("Check debug_html folder for saved HTML pages")

    logger.info("=" * 60)
    logger.info("Test completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
