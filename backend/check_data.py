"""Script to check collected data"""
from app.core.database import SessionLocal
from app.db.models import Complaint
import json

db = SessionLocal()

# Get total count
total = db.query(Complaint).count()
print(f"Total de reclamações: {total}\n")

# Get a sample complaint
complaint = db.query(Complaint).first()

if complaint:
    print("=== EXEMPLO DE RECLAMAÇÃO ===\n")
    print(f"ID: {complaint.id}")
    print(f"Título: {complaint.title[:80] if complaint.title else 'N/A'}...")
    print(f"Texto: {complaint.text[:150] if complaint.text else 'N/A'}...")
    print(f"Autor: {complaint.user_name}")
    print(f"Localização: {complaint.location}")
    print(f"Status: {complaint.status}")
    print(f"Categoria: {complaint.category}")
    print(f"Data da reclamação: {complaint.complaint_date}")
    print(f"\nResposta da empresa: {complaint.company_response_text[:100] if complaint.company_response_text else 'Sem resposta'}...")
    print(f"Data da resposta: {complaint.company_response_date}")
    print(f"Avaliação do cliente: {complaint.customer_evaluation}")
    print(f"\n=== ANÁLISE ===")
    print(f"Sentimento: {complaint.sentiment}")
    print(f"Score de sentimento: {complaint.sentiment_score}")
    print(f"Score de urgência: {complaint.urgency_score}")
    print(f"Classificação: {complaint.classification}")
    print(f"\n=== METADADOS ===")
    print(f"Coletado em: {complaint.scraped_at}")
    print(f"Analisado em: {complaint.analyzed_at}")

# Get statistics
print("\n\n=== ESTATÍSTICAS ===\n")

# Count by status
from sqlalchemy import func
status_counts = db.query(Complaint.status, func.count(Complaint.id)).group_by(Complaint.status).all()
print("Por Status:")
for status, count in status_counts:
    print(f"  {status}: {count}")

# Count by category
category_counts = db.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).all()
print("\nPor Categoria:")
for category, count in category_counts:
    print(f"  {category}: {count}")

# Count by location
location_counts = db.query(Complaint.location, func.count(Complaint.id)).group_by(Complaint.location).all()
print("\nPor Localização:")
for location, count in location_counts:
    print(f"  {location}: {count}")

# Count analyzed vs not analyzed
analyzed = db.query(Complaint).filter(Complaint.sentiment != None).count()
not_analyzed = total - analyzed
print(f"\nAnalisadas: {analyzed}")
print(f"Não analisadas: {not_analyzed}")

# Count with company response
with_response = db.query(Complaint).filter(Complaint.company_response_text != None).count()
without_response = total - with_response
print(f"\nCom resposta da empresa: {with_response}")
print(f"Sem resposta da empresa: {without_response}")

db.close()
