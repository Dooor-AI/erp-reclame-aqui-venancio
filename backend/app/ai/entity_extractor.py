"""
Entity extraction module for complaints
"""
import json
from app.ai.gemini_client import GeminiClient
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

ENTITY_PROMPT = """Extraia as seguintes entidades da reclamaï¿½ï¿½o:
- produto: nome do produto mencionado
- loja: nome da loja/unidade mencionada
- funcionario: nome de funcionï¿½rio mencionado (se houver)
- outros: outras entidades relevantes

Retorne JSON:
{
  "produto": "nome do produto",
  "loja": "nome da loja",
  "funcionario": null,
  "outros": ["entidade1", "entidade2"]
}

Se nï¿½o encontrar, use null. Responda APENAS com o JSON."""


class EntityExtractor:
    """Extracts named entities from complaints using Gemini API"""

    def __init__(self):
        self.client = GeminiClient()

    async def extract(self, text: str) -> Dict[str, any]:
        """
        Extrair entidades de uma reclamaï¿½ï¿½o

        Args:
            text: Texto da reclamaï¿½ï¿½o

        Returns:
            Dict contendo:
                - produto: Optional[str] (nome do produto)
                - loja: Optional[str] (nome da loja)
                - funcionario: Optional[str] (nome do funcionï¿½rio)
                - outros: List[str] (outras entidades)
        """
        try:
            response = await self.client.analyze_text(ENTITY_PROMPT, text)

            # Parse JSON response
            result = json.loads(response)

            return {
                'produto': result.get('produto'),
                'loja': result.get('loja'),
                'funcionario': result.get('funcionario'),
                'outros': result.get('outros', [])
            }
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da resposta: {e}\nResposta: {response}")
            # Fallback para estrutura vazia
            return {
                'produto': None,
                'loja': None,
                'funcionario': None,
                'outros': []
            }
        except Exception as e:
            logger.error(f"Erro na extraï¿½ï¿½o de entidades: {e}")
            raise
