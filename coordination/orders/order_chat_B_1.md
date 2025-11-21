# 📋 Order for Chat B - Round 1

**From:** Commander
**To:** Chat B
**Date:** 2025-11-17
**Priority:** 🔴 Critical
**Estimated Duration:** 8-10 hours (Dias 2-3)

---

## 🎯 Mission

Implementar análise de sentimento e classificação automática de reclamações usando Anthropic Claude API.

---

## 📋 Background

As reclamações coletadas pelo Chat A precisam ser analisadas para:
- Identificar sentimento (Negativo/Neutro/Positivo)
- Classificar por tipo (produto, atendimento, entrega, preço, outros)
- Extrair entidades (produto mencionado, loja, funcionário)
- Calcular score de urgência (0-10)

**Dependencies:**
- ⚠️ **Chat A deve estar em 50%** (dados disponíveis para testar)
- ✅ Acesso à API do Claude (verificar créditos)

---

## 🚀 Your Tasks

### Task 1: Integração com API Claude (2h)

**Steps:**

1. Adicionar ao `requirements.txt`:
```
anthropic==0.8.1
```

2. Criar `app/ai/claude_client.py`:
```python
from anthropic import Anthropic
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    async def analyze_text(self, prompt: str, text: str) -> str:
        """Análise de texto genérica"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nTexto:\n{text}"
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Erro na API Claude: {e}")
            raise
```

3. Adicionar no `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

4. Testar conexão com API

**Expected Result:**
- ✅ Claude API integrada
- ✅ Wrapper funcional
- ✅ Tratamento de erros

---

### Task 2: Análise de Sentimento (2h)

**Criar:** `app/ai/sentiment_analyzer.py`

```python
import json
from app.ai.claude_client import ClaudeClient
from typing import Tuple

SENTIMENT_PROMPT = """Analise o sentimento da seguinte reclamação de cliente.

Retorne um JSON com:
- sentiment: "Negativo", "Neutro" ou "Positivo"
- score: número de 0 a 10 (0=muito negativo, 5=neutro, 10=muito positivo)
- reasoning: breve justificativa (1 frase)

Responda APENAS com o JSON, sem texto adicional."""

class SentimentAnalyzer:
    def __init__(self):
        self.client = ClaudeClient()

    async def analyze(self, text: str) -> dict:
        """Analisar sentimento"""
        response = await self.client.analyze_text(SENTIMENT_PROMPT, text)

        # Parse JSON
        result = json.loads(response)

        return {
            'sentiment': result['sentiment'],
            'sentiment_score': result['score'],
            'reasoning': result.get('reasoning', '')
        }
```

**Validação:**
- Testar com 10-20 reclamações
- Validar manualmente
- Acurácia >= 80%

**Expected Result:**
- ✅ Análise de sentimento funcionando
- ✅ Formato JSON validado
- ✅ 80%+ acurácia

---

### Task 3: Classificação de Tipo (2h)

**Criar:** `app/ai/classifier.py`

```python
CLASSIFICATION_PROMPT = """Classifique a reclamação abaixo nas seguintes categorias:
- produto: problema com produto (defeito, qualidade, etc)
- atendimento: problema com atendimento (rude, ineficiente, etc)
- entrega: problema com entrega (atraso, extravio, etc)
- preco: problema com preço/cobrança
- outros: outros tipos de problemas

Pode haver múltiplas categorias. Retorne JSON:
{
  "categories": ["categoria1", "categoria2"],
  "primary_category": "categoria_principal",
  "confidence": 0.9
}

Responda APENAS com o JSON."""

class Classifier:
    def __init__(self):
        self.client = ClaudeClient()

    async def classify(self, text: str) -> dict:
        response = await self.client.analyze_text(CLASSIFICATION_PROMPT, text)
        result = json.loads(response)

        return {
            'categories': result['categories'],
            'primary_category': result['primary_category'],
            'confidence': result.get('confidence', 0.0)
        }
```

**Expected Result:**
- ✅ Classificação funcionando
- ✅ Múltiplas categorias suportadas
- ✅ Validação manual OK

---

### Task 4: Extração de Entidades (2h)

**Criar:** `app/ai/entity_extractor.py`

```python
ENTITY_PROMPT = """Extraia as seguintes entidades da reclamação:
- produto: nome do produto mencionado
- loja: nome da loja/unidade mencionada
- funcionario: nome de funcionário mencionado (se houver)
- outros: outras entidades relevantes

Retorne JSON:
{
  "produto": "nome do produto",
  "loja": "nome da loja",
  "funcionario": null,
  "outros": ["entidade1", "entidade2"]
}

Se não encontrar, use null. Responda APENAS com o JSON."""

class EntityExtractor:
    def __init__(self):
        self.client = ClaudeClient()

    async def extract(self, text: str) -> dict:
        response = await self.client.analyze_text(ENTITY_PROMPT, text)
        return json.loads(response)
```

**Expected Result:**
- ✅ Extração de entidades funcionando
- ✅ Estrutura JSON validada

---

### Task 5: Score de Urgência (1h)

**Criar:** `app/ai/urgency_scorer.py`

```python
class UrgencyScorer:
    URGENT_KEYWORDS = [
        'processual', 'judicial', 'procon', 'advogado',
        'processo', 'ação', 'justiça', 'urgente',
        'imediato', 'grave', 'sério', 'inadmissível'
    ]

    def calculate_score(self, text: str, sentiment_score: float) -> float:
        """Calcular urgência (0-10)"""
        score = 0.0

        # Base: inversão do sentiment (negativo = urgente)
        score += (10 - sentiment_score) * 0.5

        # Keywords
        text_lower = text.lower()
        keyword_count = sum(1 for kw in self.URGENT_KEYWORDS if kw in text_lower)
        score += min(keyword_count * 1.5, 5.0)

        return min(score, 10.0)
```

**Expected Result:**
- ✅ Score de urgência calculado
- ✅ Baseado em sentimento + keywords

---

### Task 6: Pipeline Completo + API (1h)

**Criar:** `app/services/analysis_service.py`

```python
from app.ai.sentiment_analyzer import SentimentAnalyzer
from app.ai.classifier import Classifier
from app.ai.entity_extractor import EntityExtractor
from app.ai.urgency_scorer import UrgencyScorer
from app.db.crud import update_complaint_analysis
from sqlalchemy.orm import Session

class AnalysisService:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.classifier = Classifier()
        self.entity_extractor = EntityExtractor()
        self.urgency_scorer = UrgencyScorer()

    async def analyze_complaint(self, db: Session, complaint_id: int):
        """Pipeline completo de análise"""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise ValueError("Complaint not found")

        text = f"{complaint.title}\n\n{complaint.text}"

        # 1. Sentimento
        sentiment_result = await self.sentiment_analyzer.analyze(text)

        # 2. Classificação
        classification_result = await self.classifier.classify(text)

        # 3. Entidades
        entities = await self.entity_extractor.extract(text)

        # 4. Urgência
        urgency = self.urgency_scorer.calculate_score(
            text,
            sentiment_result['sentiment_score']
        )

        # Atualizar banco
        update_complaint_analysis(
            db,
            complaint_id,
            sentiment=sentiment_result['sentiment'],
            sentiment_score=sentiment_result['sentiment_score'],
            classification=classification_result['categories'],
            entities=entities,
            urgency_score=urgency
        )

        return {
            "complaint_id": complaint_id,
            "sentiment": sentiment_result,
            "classification": classification_result,
            "entities": entities,
            "urgency_score": urgency
        }
```

**Criar endpoints** em `app/api/endpoints/analytics.py`:

```python
from fastapi import APIRouter, Depends
from app.services.analysis_service import AnalysisService
from app.core.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/analyze/{complaint_id}")
async def analyze_complaint(complaint_id: int, db: Session = Depends(get_db)):
    service = AnalysisService()
    result = await service.analyze_complaint(db, complaint_id)
    return result

@router.post("/analyze/batch")
async def analyze_batch(db: Session = Depends(get_db)):
    """Analisar todas as reclamações não analisadas"""
    complaints = db.query(Complaint).filter(Complaint.sentiment == None).all()

    service = AnalysisService()
    results = []

    for complaint in complaints:
        try:
            result = await service.analyze_complaint(db, complaint.id)
            results.append(result)
        except Exception as e:
            logger.error(f"Erro ao analisar {complaint.id}: {e}")

    return {"analyzed": len(results), "total": len(complaints)}

@router.get("/stats/sentiment")
async def sentiment_stats(db: Session = Depends(get_db)):
    """Estatísticas de sentimento"""
    stats = db.query(
        Complaint.sentiment,
        func.count(Complaint.id),
        func.avg(Complaint.sentiment_score)
    ).group_by(Complaint.sentiment).all()

    return {
        "by_sentiment": [
            {"sentiment": s[0], "count": s[1], "avg_score": s[2]}
            for s in stats
        ]
    }

@router.get("/stats/categories")
async def category_stats(db: Session = Depends(get_db)):
    """Top 5 categorias"""
    # Implementar contagem de categorias do JSON
    pass

@router.get("/stats/urgency")
async def urgency_stats(db: Session = Depends(get_db)):
    """Reclamações mais urgentes"""
    urgent = db.query(Complaint).filter(
        Complaint.urgency_score >= 7.0
    ).order_by(Complaint.urgency_score.desc()).limit(10).all()

    return {"urgent_complaints": urgent}
```

**Registrar router** em `main.py`

**Expected Result:**
- ✅ Pipeline completo funcionando
- ✅ Endpoint de análise individual
- ✅ Endpoint de análise em lote
- ✅ Endpoints de estatísticas

---

## 📝 Deliverables

1. **`answer_chat_B_1.md`** - Your results
2. **Backend code** - All AI modules and endpoints
3. **Sample analysis** - 10-15 reclamações analisadas com validação manual

**Answer File Must Include:**

- Status (✅ Complete / 🔄 In Progress / ⚠️ Blocked)
- Summary of what was done
- Analysis accuracy validation (>=80%)
- Number of complaints analyzed
- API endpoints implemented
- Sample results
- Issues encountered
- Time tracking summary

---

## ⏰ Time Tracking

```markdown
# Chat B - Round 1 - Time Tracking

**Started:** [HH:MM]
**Estimated Duration:** 8-10 hours
**Expected Completion:** [HH:MM] (Day 3 EOD)
**Timeout Threshold:** [HH:MM] (ETA + 10%)

| Task | Estimated | Actual | Status |
|------|-----------|--------|--------|
| Task 1: Claude API | 2h | - | ⏳ |
| Task 2: Sentiment | 2h | - | ⏳ |
| Task 3: Classification | 2h | - | ⏳ |
| Task 4: Entities | 2h | - | ⏳ |
| Task 5: Urgency | 1h | - | ⏳ |
| Task 6: Pipeline | 1h | - | ⏳ |
```

---

## 🎯 Success Criteria

- ✅ Claude API integrada e funcionando
- ✅ Análise de sentimento com 80%+ acurácia (validação manual)
- ✅ Classificação por categorias funcionando
- ✅ Extração de entidades implementada
- ✅ Score de urgência calculado
- ✅ Pipeline completo rodando
- ✅ Endpoints de analytics criados
- ✅ Documentação dos prompts

---

## 📞 Questions?

If you encounter:

- **Claude API errors** → Check API key, rate limits, create alert
- **JSON parsing issues** → Adjust prompts, add validation
- **Low accuracy (<80%)** → Refine prompts, test more examples
- **Rate limiting** → Implement caching, reduce calls
- **Chat A not ready** → Create `question_B_to_A_1.md` or wait for checkpoint

---

## 🔄 Related Tasks

- **Chat A** provides the data you need
- **Chat C** (Response Generator) depends on your analysis
- **Chat D** (Dashboard) will display your statistics
- **Chat E** will document your AI prompts

**At 100% completion**, create `coordination/alerts/checkpoint_B_100.md` to notify Chat C can start.

---

**Start when Chat A reaches 50%! Good luck! 🚀**

**Remember:** Your analysis quality determines response quality. Take time to validate!
