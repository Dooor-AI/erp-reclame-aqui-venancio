"""
Auto-analyze script - monitors DB and runs AI analysis on new complaints
Runs analysis every time 5 new unanalyzed complaints are detected
"""
import time
import requests
import logging
from app.core.database import SessionLocal
from app.db.models import Complaint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://localhost:3003/analytics/analyze/batch"
CHECK_INTERVAL = 10  # seconds between checks
BATCH_SIZE = 5  # analyze when this many new complaints exist

def get_counts():
    """Get total and analyzed complaint counts"""
    db = SessionLocal()
    try:
        total = db.query(Complaint).count()
        analyzed = db.query(Complaint).filter(Complaint.sentiment != None).count()
        return total, analyzed
    finally:
        db.close()

def run_analysis(limit):
    """Run AI analysis via API"""
    try:
        response = requests.post(f"{API_URL}?limit={limit}", timeout=120)
        if response.status_code == 200:
            result = response.json()
            return result.get('analyzed', 0)
        else:
            logger.error(f"API error: {response.status_code}")
            return 0
    except Exception as e:
        logger.error(f"Request error: {e}")
        return 0

def main():
    print("=" * 60)
    print("AUTO-ANALYZE - Monitoring for new complaints")
    print("=" * 60)
    print(f"Will analyze every {BATCH_SIZE} new unanalyzed complaints")
    print(f"Checking every {CHECK_INTERVAL} seconds")
    print("=" * 60)
    print()

    last_analyzed_count = 0
    total_analyzed_this_session = 0

    while True:
        try:
            total, analyzed = get_counts()
            unanalyzed = total - analyzed

            if unanalyzed >= BATCH_SIZE:
                logger.info(f"Found {unanalyzed} unanalyzed complaints - running analysis...")

                # Analyze in batches
                newly_analyzed = run_analysis(unanalyzed)
                total_analyzed_this_session += newly_analyzed

                logger.info(f"Analyzed {newly_analyzed} complaints")
                logger.info(f"Session total: {total_analyzed_this_session}")

                # Update counts
                total, analyzed = get_counts()

            # Status update
            logger.info(f"DB: {total} total, {analyzed} analyzed, {total - analyzed} pending")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\nStopping auto-analyze...")
            print(f"Total analyzed this session: {total_analyzed_this_session}")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
