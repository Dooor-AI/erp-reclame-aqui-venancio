"""
Urgency scoring module for complaints
"""
import logging

logger = logging.getLogger(__name__)


class UrgencyScorer:
    """Calculates urgency score for complaints based on sentiment and keywords"""

    URGENT_KEYWORDS = [
        'processual', 'judicial', 'procon', 'advogado',
        'processo', 'aÃ§Ã£o', 'justiÃ§a', 'urgente',
        'imediato', 'grave', 'sÃ©rio', 'inadmissÃ­vel',
        'inaceitÃ¡vel', 'absurdo', 'revoltante', 'escandaloso',
        'fraude', 'enganaÃ§Ã£o', 'golpe', 'roubo',
        'lesÃ£o', 'prejuÃ­zo', 'dano', 'consumidor'
    ]

    def calculate_score(self, text: str, sentiment_score: float) -> float:
        """
        Calcular score de urgÃªncia (0-10)

        Args:
            text: Texto da reclamaÃ§Ã£o
            sentiment_score: Score de sentimento (0-10, onde 0 Ã© muito negativo)

        Returns:
            float: Score de urgÃªncia de 0 a 10 (10 = mais urgente)

        Formula:
            - Base: inversÃ£o do sentiment (negativo = urgente)
            - Keywords: +1.5 pontos por keyword encontrada (mÃ¡ximo +5.0)
            - MÃ¡ximo: 10.0
        """
        score = 0.0

        # Base: inversÃ£o do sentiment (quanto mais negativo, mais urgente)
        score += (10 - sentiment_score) * 0.5

        # Keywords urgentes
        text_lower = text.lower()
        keyword_count = sum(1 for kw in self.URGENT_KEYWORDS if kw in text_lower)
        score += min(keyword_count * 1.5, 5.0)

        # Garantir que estÃ¡ no range 0-10
        return min(max(score, 0.0), 10.0)
