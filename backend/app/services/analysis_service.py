"""
Analysis service - Complete pipeline for complaint analysis
"""
from app.ai.sentiment_analyzer import SentimentAnalyzer
from app.ai.classifier import Classifier
from app.ai.entity_extractor import EntityExtractor
from app.ai.urgency_scorer import UrgencyScorer
from app.ai.store_type_classifier import StoreTypeClassifier
from app.ai.smart_tagger import SmartTagger
from app.db.crud import update_complaint_analysis, get_complaint
from app.db.models import Complaint
from sqlalchemy.orm import Session
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AnalysisService:
    """Complete analysis pipeline for complaints"""

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.classifier = Classifier()
        self.entity_extractor = EntityExtractor()
        self.urgency_scorer = UrgencyScorer()
        self.store_type_classifier = StoreTypeClassifier()
        self.smart_tagger = SmartTagger()

    async def analyze_complaint(self, db: Session, complaint_id: int) -> Dict:
        """
        Pipeline completo de anÃ¡lise de uma reclamaÃ§Ã£o

        Args:
            db: Database session
            complaint_id: ID da reclamaÃ§Ã£o

        Returns:
            Dict com todos os resultados da anÃ¡lise

        Raises:
            ValueError: Se a reclamaÃ§Ã£o nÃ£o for encontrada
            Exception: Se houver erro na anÃ¡lise
        """
        # Get complaint
        complaint = get_complaint(db, complaint_id)
        if not complaint:
            raise ValueError(f"Complaint {complaint_id} not found")

        logger.info(f"Starting analysis for complaint {complaint_id}")

        # Combine title and text for analysis
        text = f"{complaint.title}\n\n{complaint.text}" if complaint.title else complaint.text

        try:
            # 1. Sentiment Analysis
            logger.info(f"Analyzing sentiment for complaint {complaint_id}")
            sentiment_result = await self.sentiment_analyzer.analyze(text)

            # 2. Classification
            logger.info(f"Classifying complaint {complaint_id}")
            classification_result = await self.classifier.classify(text)

            # 3. Entity Extraction
            logger.info(f"Extracting entities from complaint {complaint_id}")
            entities = await self.entity_extractor.extract(text)

            # 4. Urgency Score
            logger.info(f"Calculating urgency for complaint {complaint_id}")
            urgency = self.urgency_scorer.calculate_score(
                text,
                sentiment_result['sentiment_score']
            )

            # 5. Store Type Classification (physical vs online)
            logger.info(f"Classifying store type for complaint {complaint_id}")
            store_type_result = await self.store_type_classifier.classify(text)

            # 6. Smart Tags (middle distribution)
            logger.info(f"Generating smart tags for complaint {complaint_id}")
            tags_result = await self.smart_tagger.generate_tags(text, complaint.title)

            # Update database
            logger.info(f"Updating database for complaint {complaint_id}")
            update_complaint_analysis(
                db,
                complaint_id,
                sentiment=sentiment_result['sentiment'],
                sentiment_score=sentiment_result['sentiment_score'],
                classification=classification_result['categories'],
                entities=entities,
                urgency_score=urgency,
                store_type=store_type_result['store_type'],
                tags=tags_result['tags']
            )

            logger.info(f"Analysis complete for complaint {complaint_id}")

            return {
                "complaint_id": complaint_id,
                "sentiment": sentiment_result,
                "classification": classification_result,
                "entities": entities,
                "urgency_score": urgency,
                "store_type": store_type_result,
                "tags": tags_result,
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"Error analyzing complaint {complaint_id}: {e}")
            raise

    async def analyze_batch(
        self,
        db: Session,
        limit: Optional[int] = None
    ) -> Dict:
        """
        Analisar mÃºltiplas reclamaÃ§Ãµes nÃ£o analisadas

        Args:
            db: Database session
            limit: NÃºmero mÃ¡ximo de reclamaÃ§Ãµes a analisar (None = todas)

        Returns:
            Dict com estatÃ­sticas da anÃ¡lise em lote
        """
        # Get unanalyzed complaints
        query = db.query(Complaint).filter(Complaint.sentiment == None)
        if limit:
            query = query.limit(limit)

        complaints = query.all()
        total = len(complaints)

        logger.info(f"Starting batch analysis for {total} complaints")

        results = []
        errors = []

        for complaint in complaints:
            try:
                result = await self.analyze_complaint(db, complaint.id)
                results.append(result)
                logger.info(f"Successfully analyzed complaint {complaint.id}")
            except Exception as e:
                logger.error(f"Error analyzing complaint {complaint.id}: {e}")
                errors.append({
                    "complaint_id": complaint.id,
                    "error": str(e)
                })

        logger.info(f"Batch analysis complete: {len(results)}/{total} successful")

        return {
            "total_processed": total,
            "successful": len(results),
            "failed": len(errors),
            "success_rate": len(results) / total if total > 0 else 0,
            "results": results,
            "errors": errors
        }
