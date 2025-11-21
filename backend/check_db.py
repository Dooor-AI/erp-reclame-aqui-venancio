"""Check database status"""
from app.core.database import SessionLocal
from app.db.models import Complaint

db = SessionLocal()
total = db.query(Complaint).count()
analyzed = db.query(Complaint).filter(Complaint.sentiment != None).count()

print(f"Total complaints: {total}")
print(f"Analyzed: {analyzed}")

# Show sample
if total > 0:
    sample = db.query(Complaint).first()
    print(f"\nSample complaint:")
    print(f"  Title: {sample.title[:50]}...")
    print(f"  Sentiment: {sample.sentiment}")
    print(f"  Classification: {sample.classification}")

db.close()
