"""
Script to analyze complaint data in database
"""
from app.core.database import SessionLocal
from app.db.models import Complaint
from collections import Counter

db = SessionLocal()

# Get statistics
total = db.query(Complaint).count()
with_external_id = db.query(Complaint).filter(Complaint.external_id.isnot(None)).count()
test_data = db.query(Complaint).filter(Complaint.external_id.like('TEST_%')).count()
real_scraped = with_external_id - test_data

print(f'='*70)
print(f'DATABASE STATISTICS')
print(f'='*70)
print(f'Total complaints: {total}')
print(f'With external_id: {with_external_id}')
print(f'TEST/Mock data: {test_data}')
print(f'Real scraped data: {real_scraped}')
print()

# Check what data we have
all_complaints = db.query(Complaint).all()

# Analyze external IDs
external_ids = [c.external_id for c in all_complaints if c.external_id]
print(f'External IDs found: {len(external_ids)}')
print(f'Unique external IDs: {len(set(external_ids))}')
print()

# Check for location data
locations = [c.location for c in all_complaints if c.location]
print(f'Complaints with location: {len(locations)}')
if locations:
    location_counts = Counter(locations)
    print('Top locations:')
    for loc, count in location_counts.most_common(10):
        print(f'  {loc}: {count}')
print()

# Check for categories
categories_field = [c.category for c in all_complaints if c.category]
print(f'Complaints with category field: {len(categories_field)}')
if categories_field:
    category_counts = Counter(categories_field)
    print('Categories from field:')
    for cat, count in category_counts.most_common(10):
        print(f'  {cat}: {count}')
print()

# Check dates
with_dates = [c for c in all_complaints if c.complaint_date]
print(f'Complaints with complaint_date: {len(with_dates)}')
if with_dates:
    dates = [c.complaint_date for c in with_dates]
    print(f'Oldest: {min(dates)}')
    print(f'Newest: {max(dates)}')
print()

# Show sample of real data (if exists)
print(f'='*70)
print(f'SAMPLE OF DATA (first 3)')
print(f'='*70)
for c in all_complaints[:3]:
    print(f'\nID: {c.id}')
    print(f'Title: {c.title}')
    print(f'External ID: {c.external_id}')
    print(f'Status: {c.status}')
    print(f'Category: {c.category}')
    print(f'Location: {c.location}')
    print(f'Date: {c.complaint_date}')
    print(f'Text: {c.text[:100]}...')

db.close()
