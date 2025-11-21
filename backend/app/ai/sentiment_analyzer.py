"""
Sentiment analysis module for complaint classification
"""
import json
from app.ai.gemini_client import GeminiClient
from typing import Dict
import logging

logger = logging.getLogger(__name__)

SENTIMENT_PROMPT = """Analise o sentimento da seguinte reclamaï¿½ï¿½o de cliente.

Retorne um JSON com:
- sentiment: "Negativo", "Neutro" ou "Positivo"
- score: nï¿½mero de 0 a 10 (0=muito negativo, 5=neutro, 10=muito positivo)
- reasoning: breve justificativa (1 frase)

Responda APENAS com o JSON, sem texto adicional."""


class SentimentAnalyzer:
    """Analyzes sentiment of customer complaints using Gemini API"""

    def __init__(self):
        self.client = GeminiClient()

    async def analyze(self, text: str) -> Dict[str, any]:
        """
        Analisar sentimento de uma reclamaï¿½ï¿½o

        Args:
            text: Texto da reclamaï¿½ï¿½o

        Returns:
            Dict contendo:
                - sentiment: string ("Negativo", "Neutro", "Positivo")
                - sentiment_score: float (0-10)
                - reasoning: string (justificativa)
        """
        try:
            response = await self.client.analyze_text(SENTIMENT_PROMPT, text)

            # Parse JSON response
            result = json.loads(response)

            return {
                'sentiment': result['sentiment'],
                'sentiment_score': float(result['score']),
                'reasoning': result.get('reasoning', '')
            }
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da resposta: {e}\nResposta: {response}")
            # Fallback para sentimento neutro
            return {
                'sentiment': 'Neutro',
                'sentiment_score': 5.0,
                'reasoning': 'Erro ao processar anï¿½lise'
            }
        except Exception as e:
            logger.error(f"Erro na anï¿½lise de sentimento: {e}")
            raise
