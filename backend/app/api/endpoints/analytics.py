"""
Analytics endpoints for complaint analysis
Route order: batch routes must come before parameterized routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.core.database import get_db
from app.services.analysis_service import AnalysisService
from app.db.models import Complaint
from typing import Optional
from datetime import datetime, timedelta
from collections import Counter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/analyze/batch")
async def analyze_batch(
    limit: Optional[int] = Query(None, description="Limite de reclamações a analisar"),
    db: Session = Depends(get_db)
):
    """
    Analisar todas as reclamações não analisadas (ou até o limite especificado)

    Retorna estatísticas sobre o processo de análise em lote.
    """
    try:
        service = AnalysisService()
        result = await service.analyze_batch(db, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis error: {str(e)}")


@router.post("/analyze/{complaint_id}")
async def analyze_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """
    Analisar uma reclamação específica

    Executa o pipeline completo:
    - Análise de sentimento
    - Classificação por categoria
    - Extração de entidades
    - Cálculo de score de urgência
    """
    try:
        service = AnalysisService()
        result = await service.analyze_complaint(db, complaint_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing complaint {complaint_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/stats/sentiment")
async def sentiment_stats(db: Session = Depends(get_db)):
    """
    EstatÃ­sticas de sentimento

    Retorna contagem e score mÃ©dio por sentimento (Negativo, Neutro, Positivo)
    """
    try:
        stats = db.query(
            Complaint.sentiment,
            func.count(Complaint.id).label('count'),
            func.avg(Complaint.sentiment_score).label('avg_score'),
            func.min(Complaint.sentiment_score).label('min_score'),
            func.max(Complaint.sentiment_score).label('max_score')
        ).filter(
            Complaint.sentiment.isnot(None)
        ).group_by(Complaint.sentiment).all()

        total_analyzed = sum(s.count for s in stats)

        return {
            "total_analyzed": total_analyzed,
            "by_sentiment": [
                {
                    "sentiment": s.sentiment,
                    "count": s.count,
                    "percentage": round((s.count / total_analyzed * 100) if total_analyzed > 0 else 0, 2),
                    "avg_score": round(float(s.avg_score), 2) if s.avg_score else 0,
                    "min_score": round(float(s.min_score), 2) if s.min_score else 0,
                    "max_score": round(float(s.max_score), 2) if s.max_score else 0
                }
                for s in stats
            ]
        }
    except Exception as e:
        logger.error(f"Error getting sentiment stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/categories")
async def category_stats(db: Session = Depends(get_db)):
    """
    EstatÃ­sticas de categorias

    Retorna contagem de reclamaÃ§Ãµes por categoria
    (incluindo categorias mÃºltiplas)
    """
    try:
        # Get all complaints with classification
        complaints = db.query(Complaint).filter(
            Complaint.classification.isnot(None)
        ).all()

        # Count categories
        category_counts = {}
        for complaint in complaints:
            if complaint.classification:
                for category in complaint.classification:
                    category_counts[category] = category_counts.get(category, 0) + 1

        # Sort by count descending
        sorted_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        total = len(complaints)

        return {
            "total_classified": total,
            "categories": [
                {
                    "category": cat,
                    "count": count,
                    "percentage": round((count / total * 100) if total > 0 else 0, 2)
                }
                for cat, count in sorted_categories
            ],
            "top_5": [
                {
                    "category": cat,
                    "count": count,
                    "percentage": round((count / total * 100) if total > 0 else 0, 2)
                }
                for cat, count in sorted_categories[:5]
            ]
        }
    except Exception as e:
        logger.error(f"Error getting category stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/urgency")
async def urgency_stats(
    min_score: float = Query(7.0, description="Score mÃ­nimo de urgÃªncia"),
    limit: int = Query(10, description="NÃºmero mÃ¡ximo de resultados"),
    db: Session = Depends(get_db)
):
    """
    ReclamaÃ§Ãµes mais urgentes

    Retorna reclamaÃ§Ãµes com alto score de urgÃªncia (padrÃ£o >= 7.0)
    """
    try:
        urgent = db.query(Complaint).filter(
            Complaint.urgency_score >= min_score
        ).order_by(Complaint.urgency_score.desc()).limit(limit).all()

        # Overall urgency stats
        avg_urgency = db.query(func.avg(Complaint.urgency_score)).filter(
            Complaint.urgency_score.isnot(None)
        ).scalar() or 0

        total_urgent = db.query(func.count(Complaint.id)).filter(
            Complaint.urgency_score >= min_score
        ).scalar() or 0

        total_analyzed = db.query(func.count(Complaint.id)).filter(
            Complaint.urgency_score.isnot(None)
        ).scalar() or 0

        return {
            "avg_urgency_score": round(float(avg_urgency), 2),
            "total_urgent": total_urgent,
            "total_analyzed": total_analyzed,
            "urgent_percentage": round(
                (total_urgent / total_analyzed * 100) if total_analyzed > 0 else 0,
                2
            ),
            "urgent_complaints": [
                {
                    "id": c.id,
                    "title": c.title,
                    "urgency_score": round(c.urgency_score, 2),
                    "sentiment": c.sentiment,
                    "sentiment_score": round(c.sentiment_score, 2) if c.sentiment_score else None,
                    "categories": c.classification,
                    "complaint_date": c.complaint_date.isoformat() if c.complaint_date else None
                }
                for c in urgent
            ]
        }
    except Exception as e:
        logger.error(f"Error getting urgency stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def stats_overview(db: Session = Depends(get_db)):
    """
    VisÃ£o geral de todas as estatÃ­sticas

    Combina mÃ©tricas de sentimento, categorias, urgÃªncia e anÃ¡lise geral
    """
    try:
        total = db.query(func.count(Complaint.id)).scalar() or 0
        analyzed = db.query(func.count(Complaint.id)).filter(
            Complaint.sentiment.isnot(None)
        ).scalar() or 0
        not_analyzed = total - analyzed

        # Sentiment distribution
        sentiment_dist = db.query(
            Complaint.sentiment,
            func.count(Complaint.id)
        ).filter(
            Complaint.sentiment.isnot(None)
        ).group_by(Complaint.sentiment).all()

        # Average scores
        avg_sentiment = db.query(func.avg(Complaint.sentiment_score)).filter(
            Complaint.sentiment_score.isnot(None)
        ).scalar() or 0

        avg_urgency = db.query(func.avg(Complaint.urgency_score)).filter(
            Complaint.urgency_score.isnot(None)
        ).scalar() or 0

        return {
            "totals": {
                "total_complaints": total,
                "analyzed": analyzed,
                "not_analyzed": not_analyzed,
                "analysis_rate": round((analyzed / total * 100) if total > 0 else 0, 2)
            },
            "averages": {
                "sentiment_score": round(float(avg_sentiment), 2),
                "urgency_score": round(float(avg_urgency), 2)
            },
            "sentiment_distribution": {
                s[0]: s[1] for s in sentiment_dist
            }
        }
    except Exception as e:
        logger.error(f"Error getting overview stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/timeline")
async def timeline_stats(
    days: int = Query(30, description="Número de dias para incluir no histórico"),
    db: Session = Depends(get_db)
):
    """
    Série histórica de reclamações

    Retorna quantidade de reclamações por data para os últimos N dias
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query all complaints in date range
        complaints = db.query(Complaint).filter(
            Complaint.complaint_date >= start_date,
            Complaint.complaint_date <= end_date
        ).all()

        # Group by date
        date_counts = {}
        for complaint in complaints:
            if complaint.complaint_date:
                date_str = complaint.complaint_date.date().isoformat()
                date_counts[date_str] = date_counts.get(date_str, 0) + 1

        # Format data
        timeline_data = [
            {"date": date, "count": count}
            for date, count in sorted(date_counts.items())
        ]

        total_period = sum(item['count'] for item in timeline_data)

        return {
            "period_days": days,
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "total_complaints": total_period,
            "timeline": timeline_data
        }
    except Exception as e:
        logger.error(f"Error getting timeline stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/locations")
async def location_stats(
    limit: int = Query(20, description="Número máximo de localizações"),
    db: Session = Depends(get_db)
):
    """
    Estatísticas por localização

    Retorna distribuição geográfica das reclamações
    """
    try:
        # Query location distribution
        locations = db.query(
            Complaint.location,
            func.count(Complaint.id).label('count')
        ).filter(
            Complaint.location.isnot(None),
            Complaint.location != ''
        ).group_by(
            Complaint.location
        ).order_by(
            func.count(Complaint.id).desc()
        ).limit(limit).all()

        total_with_location = sum(loc.count for loc in locations)
        total_complaints = db.query(func.count(Complaint.id)).scalar() or 0
        no_location = total_complaints - total_with_location

        return {
            "total_complaints": total_complaints,
            "with_location": total_with_location,
            "without_location": no_location,
            "locations": {
                loc.location: loc.count
                for loc in locations
            },
            "top_10": [
                {
                    "location": loc.location,
                    "count": loc.count,
                    "percentage": round((loc.count / total_with_location * 100) if total_with_location > 0 else 0, 2)
                }
                for loc in locations[:10]
            ]
        }
    except Exception as e:
        logger.error(f"Error getting location stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/store-type")
async def store_type_stats(db: Session = Depends(get_db)):
    """
    Estatísticas por tipo de loja (física vs online)

    Retorna distribuição de reclamações entre lojas físicas e compras online
    """
    try:
        stats = db.query(
            Complaint.store_type,
            func.count(Complaint.id).label('count')
        ).filter(
            Complaint.store_type.isnot(None)
        ).group_by(Complaint.store_type).all()

        total = sum(s.count for s in stats)

        return {
            "total_classified": total,
            "by_store_type": [
                {
                    "store_type": s.store_type,
                    "count": s.count,
                    "percentage": round((s.count / total * 100) if total > 0 else 0, 2)
                }
                for s in stats
            ]
        }
    except Exception as e:
        logger.error(f"Error getting store type stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/tags")
async def tag_stats(
    limit: int = Query(30, description="Número máximo de tags"),
    db: Session = Depends(get_db)
):
    """
    Estatísticas de tags inteligentes

    Retorna distribuição de tags, focando na faixa média (nem muito comuns, nem raras)
    """
    try:
        # Get all complaints with tags
        complaints = db.query(Complaint).filter(
            Complaint.tags.isnot(None)
        ).all()

        # Count all tags
        tag_counts = {}
        for complaint in complaints:
            if complaint.tags:
                for tag in complaint.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort by count
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        total_tags = len(sorted_tags)

        # Calculate distribution ranges
        if total_tags > 0:
            # Middle distribution: between 25th and 75th percentile
            q1_idx = total_tags // 4
            q3_idx = (total_tags * 3) // 4
            middle_tags = sorted_tags[q1_idx:q3_idx] if q3_idx > q1_idx else sorted_tags
        else:
            middle_tags = []

        total_complaints = len(complaints)

        return {
            "total_tagged": total_complaints,
            "total_unique_tags": total_tags,
            "all_tags": [
                {
                    "tag": tag,
                    "count": count,
                    "percentage": round((count / total_complaints * 100) if total_complaints > 0 else 0, 2)
                }
                for tag, count in sorted_tags[:limit]
            ],
            "middle_distribution": [
                {
                    "tag": tag,
                    "count": count,
                    "percentage": round((count / total_complaints * 100) if total_complaints > 0 else 0, 2)
                }
                for tag, count in middle_tags[:20]
            ]
        }
    except Exception as e:
        logger.error(f"Error getting tag stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/weekly-trends")
async def weekly_trends(db: Session = Depends(get_db)):
    """
    Tendências da última semana

    Retorna análise de tendências comparando última semana com semana anterior
    """
    try:
        now = datetime.now()
        one_week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        # This week's complaints
        this_week = db.query(Complaint).filter(
            Complaint.complaint_date >= one_week_ago,
            Complaint.complaint_date <= now
        ).all()

        # Last week's complaints
        last_week = db.query(Complaint).filter(
            Complaint.complaint_date >= two_weeks_ago,
            Complaint.complaint_date < one_week_ago
        ).all()

        this_week_count = len(this_week)
        last_week_count = len(last_week)

        # Calculate trend
        if last_week_count > 0:
            trend_percentage = round(((this_week_count - last_week_count) / last_week_count) * 100, 2)
        else:
            trend_percentage = 100 if this_week_count > 0 else 0

        trend_direction = "up" if trend_percentage > 0 else "down" if trend_percentage < 0 else "stable"

        # Daily breakdown for this week
        daily_counts = {}
        for complaint in this_week:
            if complaint.complaint_date:
                date_str = complaint.complaint_date.date().isoformat()
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

        # Sentiment trend this week
        sentiment_counts = {"Negativo": 0, "Neutro": 0, "Positivo": 0}
        for complaint in this_week:
            if complaint.sentiment:
                sentiment_counts[complaint.sentiment] = sentiment_counts.get(complaint.sentiment, 0) + 1

        # Store type trend this week
        store_type_counts = {"physical": 0, "online": 0, "unknown": 0}
        for complaint in this_week:
            if complaint.store_type:
                store_type_counts[complaint.store_type] = store_type_counts.get(complaint.store_type, 0) + 1

        # Top tags this week
        tag_counts = {}
        for complaint in this_week:
            if complaint.tags:
                for tag in complaint.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "period": {
                "start": one_week_ago.date().isoformat(),
                "end": now.date().isoformat()
            },
            "summary": {
                "this_week": this_week_count,
                "last_week": last_week_count,
                "trend_percentage": trend_percentage,
                "trend_direction": trend_direction
            },
            "daily_breakdown": [
                {"date": date, "count": count}
                for date, count in sorted(daily_counts.items())
            ],
            "sentiment_this_week": sentiment_counts,
            "store_type_this_week": store_type_counts,
            "top_tags_this_week": [
                {"tag": tag, "count": count}
                for tag, count in top_tags
            ]
        }
    except Exception as e:
        logger.error(f"Error getting weekly trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/response-metrics")
async def response_metrics(db: Session = Depends(get_db)):
    """
    Métricas de tempo de resposta

    Retorna estatísticas sobre datas de criação e tempo médio de resposta
    """
    try:
        # Total complaints
        total = db.query(func.count(Complaint.id)).scalar() or 0

        # Complaints with response
        with_response = db.query(func.count(Complaint.id)).filter(
            Complaint.company_response_date.isnot(None)
        ).scalar() or 0

        # Calculate average response time (in hours)
        complaints_with_response = db.query(Complaint).filter(
            Complaint.complaint_date.isnot(None),
            Complaint.company_response_date.isnot(None)
        ).all()

        total_hours = 0
        valid_count = 0
        for c in complaints_with_response:
            if c.complaint_date and c.company_response_date:
                diff = c.company_response_date - c.complaint_date
                hours = diff.total_seconds() / 3600
                if hours >= 0:  # Only positive response times
                    total_hours += hours
                    valid_count += 1

        avg_response_hours = round(total_hours / valid_count, 2) if valid_count > 0 else 0

        # Response rate
        response_rate = round((with_response / total * 100) if total > 0 else 0, 2)

        # Resolved complaints (status contains "Resolvida" or "Resolvido")
        resolved_count = db.query(func.count(Complaint.id)).filter(
            Complaint.status.in_(['Resolvida', 'Resolvido'])
        ).scalar() or 0
        resolution_rate = round((resolved_count / total * 100) if total > 0 else 0, 2)

        # Oldest and newest complaint
        oldest = db.query(func.min(Complaint.complaint_date)).scalar()
        newest = db.query(func.max(Complaint.complaint_date)).scalar()

        return {
            "total_complaints": total,
            "with_response": with_response,
            "response_rate": response_rate,
            "avg_response_time_hours": avg_response_hours,
            "avg_response_time_days": round(avg_response_hours / 24, 2),
            "resolved_count": resolved_count,
            "resolution_rate": resolution_rate,
            "date_range": {
                "oldest": oldest.isoformat() if oldest else None,
                "newest": newest.isoformat() if newest else None
            }
        }
    except Exception as e:
        logger.error(f"Error getting response metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

