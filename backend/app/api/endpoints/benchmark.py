"""
Benchmark API - Endpoints for competitor analysis and benchmarking
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.db.models import Competitor, CompetitorComplaint, Complaint

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/competitors")
async def get_competitors(db: Session = Depends(get_db)):
    """Get all competitors with their metrics."""
    competitors = db.query(Competitor).order_by(desc(Competitor.score)).all()

    result = []
    for comp in competitors:
        complaint_count = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.competitor_id == comp.id
        ).count()

        result.append({
            'id': comp.id,
            'name': comp.name,
            'slug': comp.slug,
            'reputation': comp.reputation,
            'score': comp.score,
            'response_rate': comp.response_rate,
            'solution_rate': comp.solution_rate,
            'would_buy_again': comp.would_buy_again,
            'avg_response_time_hours': comp.avg_response_time_hours,
            'total_complaints': comp.total_complaints,
            'scraped_complaints': complaint_count,
            'last_updated': comp.last_updated.isoformat() if comp.last_updated else None,
        })

    return result


@router.get("/comparison")
async def get_comparison(db: Session = Depends(get_db)):
    """Compare Venâncio metrics with competitors."""
    # Get Venâncio stats
    total_venancio = db.query(Complaint).count()
    analyzed = db.query(Complaint).filter(Complaint.analyzed_at.isnot(None)).count()

    # Calculate Venâncio metrics from actual data
    resolved_statuses = ['Resolvido', 'Resolvida']
    resolved = db.query(Complaint).filter(
        Complaint.status.in_(resolved_statuses)
    ).count()

    responded = db.query(Complaint).filter(
        Complaint.company_response_text.isnot(None)
    ).count()

    venancio = {
        'name': 'Drogaria Venâncio',
        'slug': 'drogaria-venancio-site-e-televendas',
        'reputation': 'Bom',  # From Reclame Aqui
        'score': 7.3,
        'response_rate': (responded / total_venancio * 100) if total_venancio > 0 else 99.9,
        'solution_rate': (resolved / total_venancio * 100) if total_venancio > 0 else 83.0,
        'would_buy_again': 58.0,  # From Reclame Aqui
        'total_complaints': total_venancio,
        'is_venancio': True,
    }

    # Get competitors
    competitors = db.query(Competitor).order_by(desc(Competitor.score)).all()

    all_companies = [venancio]
    for comp in competitors:
        all_companies.append({
            'name': comp.name,
            'slug': comp.slug,
            'reputation': comp.reputation,
            'score': comp.score,
            'response_rate': comp.response_rate,
            'solution_rate': comp.solution_rate,
            'would_buy_again': comp.would_buy_again,
            'total_complaints': comp.total_complaints,
            'is_venancio': False,
        })

    # Calculate averages (excluding Venâncio)
    if competitors:
        avg_score = sum(c.score or 0 for c in competitors) / len(competitors)
        avg_solution = sum(c.solution_rate or 0 for c in competitors) / len(competitors)
        avg_would_buy = sum(c.would_buy_again or 0 for c in competitors) / len(competitors)
    else:
        avg_score = avg_solution = avg_would_buy = 0

    return {
        'companies': all_companies,
        'averages': {
            'score': round(avg_score, 1),
            'solution_rate': round(avg_solution, 1),
            'would_buy_again': round(avg_would_buy, 1),
        },
        'venancio_gaps': {
            'score': round(avg_score - venancio['score'], 1),
            'solution_rate': round(avg_solution - venancio['solution_rate'], 1),
            'would_buy_again': round(avg_would_buy - venancio['would_buy_again'], 1),
        }
    }


@router.get("/best-responses")
async def get_best_responses(
    competitor_id: Optional[int] = None,
    problem_category: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get best competitor responses to learn from (high customer scores)."""
    query = db.query(CompetitorComplaint).filter(
        CompetitorComplaint.company_response.isnot(None),
        CompetitorComplaint.customer_score.isnot(None),
        CompetitorComplaint.customer_score >= 8  # Only good responses
    )

    if competitor_id:
        query = query.filter(CompetitorComplaint.competitor_id == competitor_id)

    if problem_category:
        query = query.filter(CompetitorComplaint.problem_category == problem_category)

    responses = query.order_by(desc(CompetitorComplaint.customer_score)).limit(limit).all()

    result = []
    for r in responses:
        competitor = db.query(Competitor).filter(Competitor.id == r.competitor_id).first()
        result.append({
            'id': r.id,
            'competitor_name': competitor.name if competitor else 'Unknown',
            'title': r.title,
            'complaint_text': r.text,
            'company_response': r.company_response,
            'customer_evaluation': r.customer_evaluation,
            'customer_score': r.customer_score,
            'was_resolved': r.was_resolved,
            'would_buy_again': r.would_buy_again,
            'problem_category': r.problem_category,
            'response_tone': r.response_tone,
            'response_has_solution': r.response_has_solution,
            'response_has_apology': r.response_has_apology,
            'response_has_compensation': r.response_has_compensation,
        })

    return result


@router.get("/response-patterns")
async def get_response_patterns(db: Session = Depends(get_db)):
    """Analyze patterns in successful competitor responses."""
    # Get all resolved complaints with high scores
    high_score_responses = db.query(CompetitorComplaint).filter(
        CompetitorComplaint.company_response.isnot(None),
        CompetitorComplaint.customer_score >= 8,
        CompetitorComplaint.was_resolved == True
    ).all()

    total = len(high_score_responses)
    if total == 0:
        return {
            'total_analyzed': 0,
            'patterns': {},
            'recommendations': []
        }

    # Analyze patterns
    has_apology = sum(1 for r in high_score_responses if r.response_has_apology)
    has_solution = sum(1 for r in high_score_responses if r.response_has_solution)
    has_compensation = sum(1 for r in high_score_responses if r.response_has_compensation)
    has_deadline = sum(1 for r in high_score_responses if r.response_has_deadline)

    # Tone distribution
    tone_counts = {}
    for r in high_score_responses:
        if r.response_tone:
            tone_counts[r.response_tone] = tone_counts.get(r.response_tone, 0) + 1

    patterns = {
        'has_apology': round(has_apology / total * 100, 1) if total > 0 else 0,
        'has_solution': round(has_solution / total * 100, 1) if total > 0 else 0,
        'has_compensation': round(has_compensation / total * 100, 1) if total > 0 else 0,
        'has_deadline': round(has_deadline / total * 100, 1) if total > 0 else 0,
        'tone_distribution': {k: round(v/total*100, 1) for k, v in tone_counts.items()},
    }

    # Generate recommendations based on patterns
    recommendations = []
    if patterns['has_apology'] > 70:
        recommendations.append({
            'priority': 'high',
            'action': 'Sempre incluir pedido de desculpas',
            'reason': f'{patterns["has_apology"]}% das respostas bem avaliadas incluem desculpas'
        })

    if patterns['has_solution'] > 80:
        recommendations.append({
            'priority': 'high',
            'action': 'Oferecer solução concreta',
            'reason': f'{patterns["has_solution"]}% das respostas bem avaliadas apresentam solução'
        })

    if patterns['has_compensation'] > 30:
        recommendations.append({
            'priority': 'medium',
            'action': 'Considerar compensação quando apropriado',
            'reason': f'{patterns["has_compensation"]}% das respostas bem avaliadas oferecem compensação'
        })

    if patterns['has_deadline'] > 50:
        recommendations.append({
            'priority': 'high',
            'action': 'Informar prazo para resolução',
            'reason': f'{patterns["has_deadline"]}% das respostas bem avaliadas incluem prazo'
        })

    return {
        'total_analyzed': total,
        'patterns': patterns,
        'recommendations': recommendations,
    }


@router.get("/competitor/{competitor_id}/complaints")
async def get_competitor_complaints(
    competitor_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get complaints for a specific competitor."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    query = db.query(CompetitorComplaint).filter(
        CompetitorComplaint.competitor_id == competitor_id
    ).order_by(desc(CompetitorComplaint.complaint_date))

    total = query.count()
    complaints = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        'competitor': {
            'id': competitor.id,
            'name': competitor.name,
            'slug': competitor.slug,
        },
        'total': total,
        'page': page,
        'page_size': page_size,
        'complaints': [
            {
                'id': c.id,
                'title': c.title,
                'text': c.text,
                'status': c.status,
                'complaint_date': c.complaint_date.isoformat() if c.complaint_date else None,
                'company_response': c.company_response,
                'customer_evaluation': c.customer_evaluation,
                'customer_score': c.customer_score,
                'was_resolved': c.was_resolved,
                'would_buy_again': c.would_buy_again,
            }
            for c in complaints
        ]
    }


@router.get("/suggestions")
async def get_response_suggestions(
    complaint_text: str = Query(..., min_length=10),
    db: Session = Depends(get_db)
):
    """Get response suggestions based on similar competitor complaints."""
    # Find similar complaints from competitors with good resolutions
    # This is a simple keyword-based search - could be improved with embeddings

    keywords = complaint_text.lower().split()[:5]  # First 5 words

    similar = []
    for kw in keywords:
        if len(kw) > 4:  # Skip short words
            results = db.query(CompetitorComplaint).filter(
                CompetitorComplaint.text.ilike(f'%{kw}%'),
                CompetitorComplaint.company_response.isnot(None),
                CompetitorComplaint.customer_score >= 7
            ).limit(5).all()
            similar.extend(results)

    # Deduplicate and sort by score
    seen_ids = set()
    unique = []
    for c in similar:
        if c.id not in seen_ids:
            seen_ids.add(c.id)
            unique.append(c)

    unique.sort(key=lambda x: x.customer_score or 0, reverse=True)

    suggestions = []
    for c in unique[:5]:
        competitor = db.query(Competitor).filter(Competitor.id == c.competitor_id).first()
        suggestions.append({
            'competitor': competitor.name if competitor else 'Unknown',
            'original_complaint': c.title,
            'response': c.company_response,
            'customer_score': c.customer_score,
            'was_resolved': c.was_resolved,
        })

    return {
        'suggestions': suggestions,
        'best_practices': [
            'Sempre começar com pedido de desculpas sincero',
            'Apresentar solução concreta com prazo definido',
            'Oferecer canal direto para acompanhamento',
            'Finalizar reforçando compromisso com qualidade',
        ]
    }


@router.get("/stats")
async def get_benchmark_stats(db: Session = Depends(get_db)):
    """Get summary statistics for the benchmark module."""
    total_competitors = db.query(Competitor).count()
    total_complaints = db.query(CompetitorComplaint).count()

    with_response = db.query(CompetitorComplaint).filter(
        CompetitorComplaint.company_response.isnot(None)
    ).count()

    high_score = db.query(CompetitorComplaint).filter(
        CompetitorComplaint.customer_score >= 8
    ).count()

    return {
        'total_competitors': total_competitors,
        'total_complaints': total_complaints,
        'with_responses': with_response,
        'high_score_responses': high_score,
    }
