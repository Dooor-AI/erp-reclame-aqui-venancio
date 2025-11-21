"""
Validation script for AI analysis pipeline
Run this after setting up valid ANTHROPIC_API_KEY
"""
import asyncio
import json
from datetime import datetime
from app.core.database import SessionLocal
from app.db.models import Complaint
from app.services.analysis_service import AnalysisService


async def validate_analysis_pipeline():
    """
    Validate AI analysis pipeline with real data

    This script:
    1. Analyzes 20 sample complaints
    2. Displays results for manual validation
    3. Calculates accuracy metrics
    """

    print("="  * 70)
    print("AI ANALYSIS VALIDATION - Chat B Round 2")
    print("=" * 70)
    print()

    db = SessionLocal()
    service = AnalysisService()

    try:
        # Get unanalyzed complaints
        complaints = db.query(Complaint).filter(
            Complaint.sentiment == None
        ).limit(20).all()

        if len(complaints) == 0:
            print("No complaints to analyze. Create test data first:")
            print("  python create_test_data.py")
            return

        print(f"Found {len(complaints)} complaints to analyze")
        print()

        # Results storage
        results = []
        errors = []

        # Analyze each complaint
        for i, complaint in enumerate(complaints, 1):
            print(f"\n[{i}/{len(complaints)}] Analyzing complaint ID {complaint.id}")
            print(f"Title: {complaint.title}")
            print("-" * 70)

            try:
                result = await service.analyze_complaint(db, complaint.id)

                # Display results
                print(f"[OK] Analysis complete")
                print(f"  Sentiment: {result['sentiment']['sentiment']} (score: {result['sentiment']['sentiment_score']})")
                print(f"  Category: {result['classification']['primary_category']}")
                print(f"  Categories: {', '.join(result['classification']['categories'])}")
                print(f"  Urgency: {result['urgency_score']}/10")

                if result['entities']['produto']:
                    print(f"  Product: {result['entities']['produto']}")
                if result['entities']['loja']:
                    print(f"  Store: {result['entities']['loja']}")

                results.append({
                    'complaint_id': complaint.id,
                    'title': complaint.title,
                    'text_preview': complaint.text[:100] + "...",
                    'analysis': result
                })

            except Exception as e:
                print(f"[ERROR] {str(e)}")
                errors.append({
                    'complaint_id': complaint.id,
                    'error': str(e)
                })

        # Summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total processed: {len(complaints)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(errors)}")
        print(f"Success rate: {len(results)/len(complaints)*100:.1f}%")
        print()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total': len(complaints),
                'successful': len(results),
                'failed': len(errors),
                'results': results,
                'errors': errors
            }, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {filename}")
        print()
        print("=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("1. Review the analysis results above")
        print("2. For each complaint, assess if the AI analysis is correct:")
        print("   - Is the sentiment accurate?")
        print("   - Is the category correct?")
        print("   - Are entities properly extracted?")
        print("   - Is urgency score reasonable?")
        print("3. Calculate accuracy metrics:")
        print("   - Sentiment accuracy = (correct / total) * 100")
        print("   - Category accuracy = (correct primary category / total) * 100")
        print("   - Entity recall = (entities found / entities present) * 100")
        print("4. Document results in coordination/answers/validation_report_B_2.md")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    print("\nStarting validation...")
    print("Make sure ANTHROPIC_API_KEY is set in .env file")
    print()

    try:
        asyncio.run(validate_analysis_pipeline())
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
    except Exception as e:
        print(f"\nValidation failed: {e}")
        print("\nCommon issues:")
        print("- ANTHROPIC_API_KEY not set or invalid")
        print("- No internet connection")
        print("- API rate limit exceeded")
