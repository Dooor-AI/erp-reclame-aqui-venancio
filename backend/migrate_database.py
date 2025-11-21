"""
Add company response columns to existing database
"""
from app.core.database import SessionLocal, engine
from sqlalchemy import text

# SQL to add new columns
migrations = [
    "ALTER TABLE complaints ADD COLUMN company_response_text TEXT",
    "ALTER TABLE complaints ADD COLUMN company_response_date DATETIME",
    "ALTER TABLE complaints ADD COLUMN customer_evaluation VARCHAR(100)"
]

print("="*70)
print("DATABASE MIGRATION - Adding Company Response Columns")
print("="*70)
print()

with engine.connect() as conn:
    for i, sql in enumerate(migrations, 1):
        try:
            print(f"{i}. Executing: {sql[:60]}...")
            conn.execute(text(sql))
            conn.commit()
            print(f"   [OK] Column added successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"   [SKIP] Column already exists")
            else:
                print(f"   [ERROR] {e}")
                raise

print()
print("="*70)
print("[SUCCESS] Migration completed!")
print("="*70)
