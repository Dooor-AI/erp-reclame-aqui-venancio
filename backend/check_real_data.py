from app.core.database import SessionLocal
from app.db.models import Complaint

db = SessionLocal()

# Get real scraped complaints (not TEST data)
real_complaints = db.query(Complaint).filter(
    Complaint.external_id != None,
    ~Complaint.external_id.like('TEST_%')
).limit(10).all()

print(f'Found {len(real_complaints)} real scraped complaints')
print()

for c in real_complaints:
    print(f'{"="*70}')
    print(f'ID: {c.id}')
    print(f'Title: {c.title}')
    print(f'User: {c.user_name}')
    print(f'External ID: {c.external_id}')
    print(f'Status: {c.status}')
    print(f'Category: {c.category}')
    print(f'Scraped at: {c.scraped_at}')
    print(f'Text: {c.text[:250]}...')
    print()

# Check if we have scraped data from other companies
print(f'\n{"="*70}')
print('CHECKING FOR COMPANY NAME IN COMPLAINTS...')
print(f'{"="*70}')

venancio_count = 0
other_company_count = 0

for c in real_complaints:
    text_lower = c.text.lower()
    title_lower = c.title.lower()

    if 'venancio' in text_lower or 'venâncio' in text_lower or 'venancio' in title_lower:
        venancio_count += 1
    else:
        other_company_count += 1
        print(f'\nPOSSIBLE OTHER COMPANY:')
        print(f'ID: {c.id} - Title: {c.title}')
        print(f'Text preview: {c.text[:150]}')

print(f'\n{"="*70}')
print(f'Venancio mentions: {venancio_count}')
print(f'No Venancio mention: {other_company_count}')
print(f'{"="*70}')

db.close()
