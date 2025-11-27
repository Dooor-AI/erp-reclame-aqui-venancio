# -*- coding: utf-8 -*-
"""
Script para analisar e atualizar os padroes de resposta das reclamacoes de concorrentes.
Preenche os campos: response_has_apology, response_has_solution, response_has_compensation, response_has_deadline, response_tone
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.core.database import SessionLocal
from app.db.models import CompetitorComplaint

# Palavras-chave para detectar padroes
APOLOGY_KEYWORDS = [
    'desculpa', 'desculpas', 'lamentamos', 'sentimos muito', 'pedimos perdao',
    'sorry', 'apologize', 'sinceras desculpas', 'pedimos desculpas'
]

SOLUTION_KEYWORDS = [
    'solucao', 'resolver', 'resolucao', 'providencia', 'estorno', 'reembolso',
    'troca', 'substituicao', 'entrega', 'agendada', 'enviaremos', 'faremos',
    'providenciamos', 'garantimos', 'vamos resolver', 'ja estamos'
]

COMPENSATION_KEYWORDS = [
    'desconto', 'cupom', 'brinde', 'compensacao', 'credito', 'bonus',
    'cortesia', 'gratuito', 'gratis', 'oferta', 'voucher', '%', 'off'
]

DEADLINE_KEYWORDS = [
    'prazo', 'dias', 'horas', '24h', '48h', '72h', 'uteis', 'amanha',
    'em ate', 'maximo', 'dentro de', 'semana', 'imediato'
]


def analyze_response(text: str) -> dict:
    """Analisa o texto da resposta e retorna os padroes encontrados."""
    if not text:
        return {
            'has_apology': False,
            'has_solution': False,
            'has_compensation': False,
            'has_deadline': False,
            'tone': 'neutro'
        }

    text_lower = text.lower()

    has_apology = any(kw in text_lower for kw in APOLOGY_KEYWORDS)
    has_solution = any(kw in text_lower for kw in SOLUTION_KEYWORDS)
    has_compensation = any(kw in text_lower for kw in COMPENSATION_KEYWORDS)
    has_deadline = any(kw in text_lower for kw in DEADLINE_KEYWORDS)

    # Determinar tom baseado em padroes
    if has_apology and has_solution and has_compensation:
        tone = 'muito_empatico'
    elif has_apology and has_solution:
        tone = 'empatico'
    elif has_solution:
        tone = 'profissional'
    elif has_apology:
        tone = 'cordial'
    else:
        tone = 'neutro'

    return {
        'has_apology': has_apology,
        'has_solution': has_solution,
        'has_compensation': has_compensation,
        'has_deadline': has_deadline,
        'tone': tone
    }


def update_patterns():
    db = SessionLocal()
    try:
        # Get all complaints with responses
        complaints = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.isnot(None)
        ).all()

        if not complaints:
            print("No complaints with responses found!")
            return

        updated = 0
        for complaint in complaints:
            analysis = analyze_response(complaint.company_response)

            complaint.response_has_apology = analysis['has_apology']
            complaint.response_has_solution = analysis['has_solution']
            complaint.response_has_compensation = analysis['has_compensation']
            complaint.response_has_deadline = analysis['has_deadline']
            complaint.response_tone = analysis['tone']

            updated += 1
            print(f"Analyzed complaint {complaint.id}: apology={analysis['has_apology']}, solution={analysis['has_solution']}, compensation={analysis['has_compensation']}, deadline={analysis['has_deadline']}, tone={analysis['tone']}")

        db.commit()
        print(f"\nTotal analyzed: {updated}")

        # Show summary stats
        with_apology = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.response_has_apology == True
        ).count()
        with_solution = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.response_has_solution == True
        ).count()
        with_compensation = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.response_has_compensation == True
        ).count()
        with_deadline = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.response_has_deadline == True
        ).count()

        total_with_response = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.isnot(None)
        ).count()

        print(f"\n=== Padroes de Sucesso ===")
        print(f"Total com resposta: {total_with_response}")
        print(f"Com desculpas: {with_apology} ({with_apology/total_with_response*100:.1f}%)")
        print(f"Com solucao: {with_solution} ({with_solution/total_with_response*100:.1f}%)")
        print(f"Com compensacao: {with_compensation} ({with_compensation/total_with_response*100:.1f}%)")
        print(f"Com prazo: {with_deadline} ({with_deadline/total_with_response*100:.1f}%)")

    finally:
        db.close()


if __name__ == "__main__":
    update_patterns()
