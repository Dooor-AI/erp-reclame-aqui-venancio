"""
Continuous scraper that runs 24/7 by calling run_scraper.py in a loop
"""
import time
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_continuous.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_continuous_scraper():
    """
    Run scraper continuously in a loop

    - Executes run_scraper.py to scrape all available pages
    - Waits 6 hours between full cycles
    - Runs 24/7 indefinitely
    """
    cycle = 0

    while True:
        cycle += 1
        logger.info("="*70)
        logger.info(f"STARTING SCRAPER CYCLE #{cycle}")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)

        try:
            # Run the scraper script
            result = subprocess.run(
                ['python', 'run_scraper.py'],
                cwd='.',
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for each cycle
            )

            logger.info("="*70)
            logger.info(f"CYCLE #{cycle} COMPLETED")
            logger.info(f"Exit code: {result.returncode}")

            if result.returncode == 0:
                logger.info("Status: SUCCESS")
            else:
                logger.warning(f"Status: FAILED with code {result.returncode}")
                logger.warning(f"Error output: {result.stderr[-500:]}")  # Last 500 chars of error

            # Log last few lines of output
            output_lines = result.stdout.strip().split('\n')
            logger.info("Last 10 lines of output:")
            for line in output_lines[-10:]:
                logger.info(f"  {line}")
            logger.info("="*70)

        except subprocess.TimeoutExpired:
            logger.error(f"Cycle #{cycle} timed out after 1 hour!")
        except Exception as e:
            logger.error(f"Error in cycle #{cycle}: {e}", exc_info=True)
            logger.info("Continuing to next cycle despite error...")

        # Wait 6 hours before next cycle
        wait_hours = 6
        wait_seconds = wait_hours * 3600

        logger.info(f"Waiting {wait_hours} hours before next cycle...")
        next_time = datetime.fromtimestamp(time.time() + wait_seconds)
        logger.info(f"Next cycle will start at: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")

        time.sleep(wait_seconds)


if __name__ == "__main__":
    logger.info("="*70)
    logger.info("CONTINUOUS SCRAPER STARTED - RUNNING 24/7")
    logger.info("="*70)
    logger.info("Configuration:")
    logger.info("  - Target: Drogaria Venâncio")
    logger.info("  - Mode: All pages (using run_scraper.py)")
    logger.info("  - Interval: 6 hours between cycles")
    logger.info("  - Log file: scraper_continuous.log")
    logger.info("="*70)
    logger.info("")

    try:
        run_continuous_scraper()
    except KeyboardInterrupt:
        logger.info("\n" + "="*70)
        logger.info("SCRAPER STOPPED BY USER")
        logger.info("="*70)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
