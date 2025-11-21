"""
Test script for the new Playwright scraper
"""
import asyncio
import sys
from app.scraper.playwright_scraper import PlaywrightReclameAquiScraper
from app.core.config import settings

async def main():
    print("=" * 70)
    print("TESTING PLAYWRIGHT SCRAPER")
    print("=" * 70)
    print()

    # Test with 2 pages
    scraper = PlaywrightReclameAquiScraper(
        company_url=settings.RECLAME_AQUI_COMPANY_URL,
        max_pages=2,  # Test with 2 pages
        delay_min=1.0,
        delay_max=2.0,
        max_concurrent=5  # 5 parallel requests
    )

    print(f"Company URL: {settings.RECLAME_AQUI_COMPANY_URL}")
    print(f"Max pages: 2")
    print(f"Max concurrent: 5")
    print()

    # Run scraper
    complaints = await scraper.scrape_complaints(save_debug=True)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Complaints collected: {len(complaints)}")
    print(f"Errors: {len(scraper.get_errors())}")
    print()

    if scraper.get_errors():
        print("Errors encountered:")
        for error in scraper.get_errors()[:5]:
            print(f"  - {error}")
        print()

    if complaints:
        print("=" * 70)
        print("SAMPLE COMPLAINTS")
        print("=" * 70)

        for i, complaint in enumerate(complaints[:3], 1):
            print(f"\n{i}. {complaint.get('title', 'N/A')[:80]}...")
            print(f"   Category: {complaint.get('category', 'N/A')}")
            print(f"   Status: {complaint.get('status', 'N/A')}")
            print(f"   Location: {complaint.get('location', 'N/A')}")
            print(f"   User: {complaint.get('user_name', 'N/A')}")
            print(f"   Date: {complaint.get('complaint_date', 'N/A')}")
            print(f"   Text preview: {complaint.get('text', 'N/A')[:100]}...")

        # Count categories
        print("\n" + "=" * 70)
        print("CATEGORY DISTRIBUTION")
        print("=" * 70)
        categories = {}
        for complaint in complaints:
            cat = complaint.get('category', 'None')
            categories[cat] = categories.get(cat, 0) + 1

        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")

        # Calculate success rate
        with_category = sum(1 for c in complaints if c.get('category'))
        success_rate = (with_category / len(complaints)) * 100 if complaints else 0
        print(f"\nCategory extraction success rate: {success_rate:.1f}% ({with_category}/{len(complaints)})")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
