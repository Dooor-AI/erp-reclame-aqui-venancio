"""
Batch analysis script - runs independently of the API server
Analyzes complaints using Gemini AI with fixed tags
"""
import asyncio
import sys
import time
from datetime import datetime
from sqlalchemy import func

# Add parent to path
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.db.models import Complaint
from app.ai.sentiment_analyzer import SentimentAnalyzer
from app.ai.smart_tagger import SmartTagger
from app.ai.store_type_classifier import StoreTypeClassifier
from app.ai.urgency_scorer import UrgencyScorer

async def analyze_single(complaint_id: int, analyzer: SentimentAnalyzer, tagger: SmartTagger, classifier: StoreTypeClassifier, urgency: UrgencyScorer):
    """Analyze a single complaint"""
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return False

        text = f"{complaint.title or ''}\n\n{complaint.text or ''}"

        # Run all analyses
        sentiment_result = await analyzer.analyze(text)
        tag_result = await tagger.generate_tags(text, complaint.title or "")
        store_result = await classifier.classify(text)

        # Calculate urgency (sync method) based on sentiment score
        sentiment_score = sentiment_result.get('score', 5.0)
        urgency_score = urgency.calculate_score(text, sentiment_score)

        # Update complaint
        complaint.sentiment = sentiment_result.get('sentiment')
        complaint.sentiment_score = sentiment_score
        complaint.urgency_score = urgency_score
        complaint.tags = tag_result.get('tags', [])
        complaint.store_type = store_result.get('store_type')
        complaint.analyzed_at = datetime.now()

        db.commit()
        return True
    except Exception as e:
        print(f"  Error analyzing {complaint_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def batch_analyze(batch_size: int = 10, delay: float = 1.0):
    """Analyze all unanalyzed complaints in batches"""
    print("=" * 60)
    print("BATCH ANALYSIS - Fixed Tags System")
    print("=" * 60)

    # Initialize analyzers
    analyzer = SentimentAnalyzer()
    tagger = SmartTagger()
    classifier = StoreTypeClassifier()
    urgency = UrgencyScorer()

    db = SessionLocal()
    total_unanalyzed = db.query(Complaint).filter(Complaint.sentiment == None).count()
    total_all = db.query(Complaint).count()
    db.close()

    print(f"Total complaints: {total_all}")
    print(f"Unanalyzed: {total_unanalyzed}")
    print(f"Batch size: {batch_size}")
    print(f"Delay between batches: {delay}s")
    print("=" * 60)

    processed = 0
    errors = 0
    start_time = time.time()

    while True:
        # Get next batch
        db = SessionLocal()
        complaints = db.query(Complaint).filter(
            Complaint.sentiment == None
        ).limit(batch_size).all()
        complaint_ids = [c.id for c in complaints]
        db.close()

        if not complaint_ids:
            break

        print(f"\nBatch {processed // batch_size + 1}: Processing {len(complaint_ids)} complaints...")

        for cid in complaint_ids:
            success = await analyze_single(cid, analyzer, tagger, classifier, urgency)
            if success:
                processed += 1
                print(f"  [OK] Complaint {cid} analyzed ({processed}/{total_unanalyzed})")
            else:
                errors += 1
                print(f"  [FAIL] Complaint {cid} failed")

            # Small delay between individual analyses to avoid rate limiting
            await asyncio.sleep(0.5)

        # Progress report
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        remaining = (total_unanalyzed - processed) / rate if rate > 0 else 0
        print(f"  Progress: {processed}/{total_unanalyzed} ({100*processed/total_unanalyzed:.1f}%)")
        print(f"  Rate: {rate:.1f}/s | ETA: {remaining/60:.1f} min")

        # Delay between batches
        await asyncio.sleep(delay)

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("BATCH ANALYSIS COMPLETE")
    print(f"Processed: {processed}")
    print(f"Errors: {errors}")
    print(f"Time: {elapsed/60:.1f} minutes")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between batches")
    args = parser.parse_args()

    asyncio.run(batch_analyze(args.batch_size, args.delay))
