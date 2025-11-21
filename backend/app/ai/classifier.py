"""
Complaint classification module
"""
import json
from app.ai.gemini_client import GeminiClient
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """Classifique a reclamaï¿½ï¿½o abaixo nas seguintes categorias:
- produto: problema com produto (defeito, qualidade, etc)
- atendimento: problema com atendimento (rude, ineficiente, etc)
- entrega: problema com entrega (atraso, extravio, etc)
- preco: problema com preï¿½o/cobranï¿½a
- outros: outros tipos de problemas

Pode haver mï¿½ltiplas categorias. Retorne JSON:
{
  "categories": ["categoria1", "categoria2"],
  "primary_category": "categoria_principal",
  "confidence": 0.9
}

Responda APENAS com o JSON."""


class Classifier:
    """Classifies complaints into predefined categories using Gemini API"""

    def __init__(self):
        self.client = GeminiClient()

    async def classify(self, text: str) -> Dict[str, any]:
        """
        Classificar reclamaï¿½ï¿½o por tipo

        Args:
            text: Texto da reclamaï¿½ï¿½o

        Returns:
            Dict contendo:
                - categories: List[str] (lista de categorias aplicï¿½veis)
                - primary_category: str (categoria principal)
                - confidence: float (0-1, nï¿½vel de confianï¿½a)
        """
        try:
            response = await self.client.analyze_text(CLASSIFICATION_PROMPT, text)

            # Parse JSON response
            result = json.loads(response)

            return {
                'categories': result['categories'],
                'primary_category': result['primary_category'],
                'confidence': float(result.get('confidence', 0.0))
            }
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da resposta: {e}\nResposta: {response}")
            # Fallback para categoria "outros"
            return {
                'categories': ['outros'],
                'primary_category': 'outros',
                'confidence': 0.0
            }
        except Exception as e:
            logger.error(f"Erro na classificaï¿½ï¿½o: {e}")
            raise
