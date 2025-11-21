"""
Clear all complaints from database (preparing for real scraping)
"""
from app.core.database import SessionLocal
from app.db.models import Complaint, Coupon

db = SessionLocal()

# Count before deletion
total_complaints = db.query(Complaint).count()
total_coupons = db.query(Coupon).count()

print(f'='*70)
print(f'CLEARING DATABASE')
print(f'='*70)
print(f'Complaints to delete: {total_complaints}')
print(f'Coupons to delete: {total_coupons}')
print()

# Delete all coupons first (foreign key)
if total_coupons > 0:
    db.query(Coupon).delete()
    print(f'[OK] Deleted {total_coupons} coupons')

# Delete all complaints
if total_complaints > 0:
    db.query(Complaint).delete()
    print(f'[OK] Deleted {total_complaints} complaints')

# Commit changes
db.commit()

# Verify
remaining_complaints = db.query(Complaint).count()
remaining_coupons = db.query(Coupon).count()

print()
print(f'='*70)
print(f'VERIFICATION')
print(f'='*70)
print(f'Remaining complaints: {remaining_complaints}')
print(f'Remaining coupons: {remaining_coupons}')
print()

if remaining_complaints == 0 and remaining_coupons == 0:
    print('[SUCCESS] Database cleared successfully!')
else:
    print('[WARNING] Some records remain')

db.close()
