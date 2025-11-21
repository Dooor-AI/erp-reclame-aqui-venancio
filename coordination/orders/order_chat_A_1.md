# 📋 Order for Chat A - Round 1

**From:** Commander
**To:** Chat A
**Date:** 2025-11-17
**Priority:** 🔴 Critical
**Estimated Duration:** 12-16 hours (Dias 1-2)

---

## 🎯 Mission

Criar a fundação de dados do sistema: implementar scraping do Reclame Aqui, configurar banco de dados PostgreSQL/SQLite e criar API REST para acesso aos dados.

---

## 📋 Background

A Venâncio precisa monitorar reclamações no Reclame Aqui para responder adequadamente e melhorar seu score. Você é responsável por criar o sistema de coleta e armazenamento de dados que será a base de todo o projeto.

**Por que é importante:**
- Todos os outros chats (B, C, D, E) dependem dos dados que você vai coletar
- A qualidade do scraping determina a qualidade das análises posteriores
- A estrutura do banco impacta toda a arquitetura

**Dependencies:**
- ✅ Nenhuma - Você pode começar imediatamente!

---

## 🚀 Your Tasks

### Task 1: Setup do Projeto Backend (2h)

**Objective:** Criar estrutura de pastas e configurar ambiente Python

**Steps:**

1. Criar estrutura de pastas do backend:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── base.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── reclame_aqui_scraper.py
│   │   └── scheduler.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── complaints.py
│   └── schemas/
│       ├── __init__.py
│       └── complaint.py
├── tests/
│   └── __init__.py
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
└── README.md
```

2. Criar ambiente virtual:
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
```

3. Criar `requirements.txt` com dependências:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9  # PostgreSQL
aiosqlite==0.19.0       # SQLite async
pydantic==2.5.0
pydantic-settings==2.1.0
beautifulsoup4==4.12.2
selenium==4.15.2
requests==2.31.0
python-dotenv==1.0.0
alembic==1.12.1
apscheduler==3.10.4
```

4. Instalar dependências:
```bash
pip install -r requirements.txt
```

5. Criar `.env.example` e `.env`:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/venancio_rpa
# ou para SQLite: DATABASE_URL=sqlite:///./venancio.db

# Scraper
RECLAME_AQUI_COMPANY_URL=https://www.reclameaqui.com.br/empresa/venancio/
SCRAPER_DELAY_MIN=2
SCRAPER_DELAY_MAX=5
SCRAPER_MAX_PAGES=10
SCRAPER_POLLING_INTERVAL_HOURS=6

# API
API_TITLE=Venâncio RPA API
API_VERSION=1.0.0
API_HOST=0.0.0.0
API_PORT=8000
```

6. Criar `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
*.db
*.log
.pytest_cache/
.coverage
htmlcov/
```

7. Inicializar FastAPI básico em `app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.db.base import Base

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Criar tabelas
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Venâncio RPA API", "version": settings.API_VERSION}

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Expected Result:**
- ✅ Estrutura de pastas criada
- ✅ Ambiente virtual configurado
- ✅ Dependências instaladas
- ✅ FastAPI rodando em `http://localhost:8000`
- ✅ Documentação Swagger em `http://localhost:8000/docs`

---

### Task 2: Implementar Scraper do Reclame Aqui (6h)

**Objective:** Coletar reclamações do Reclame Aqui da Venâncio

**Steps:**

1. **Análise da estrutura HTML** (1h):
   - Acessar https://www.reclameaqui.com.br/empresa/venancio/
   - Inspecionar HTML das reclamações
   - Identificar seletores CSS/XPath para:
     - Título da reclamação
     - Texto completo
     - Data de publicação
     - Nome do usuário
     - Status (Respondida/Não respondida/Resolvida)
     - Categoria (se disponível)
     - Localização
     - ID da reclamação

2. **Implementar scraper base** em `app/scraper/reclame_aqui_scraper.py` (3h):

```python
import time
import random
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ReclameAquiScraper:
    def __init__(self, company_url: str, max_pages: int = 10):
        self.company_url = company_url
        self.max_pages = max_pages
        self.complaints = []

    def _get_driver(self):
        """Configurar Selenium WebDriver"""
        options = Options()
        options.add_argument('--headless')  # Rodar sem interface gráfica
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        return webdriver.Chrome(options=options)

    def _random_delay(self, min_sec=2, max_sec=5):
        """Delay aleatório para evitar detecção"""
        time.sleep(random.uniform(min_sec, max_sec))

    def scrape_complaints(self) -> List[Dict]:
        """Coletar reclamações"""
        driver = self._get_driver()

        try:
            for page in range(1, self.max_pages + 1):
                logger.info(f"Scraping página {page}/{self.max_pages}")

                # Navegar para página
                url = f"{self.company_url}lista-reclamacoes/?pagina={page}"
                driver.get(url)

                # Aguardar carregamento
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "complain"))
                )

                # Parse HTML
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Extrair reclamações (ajustar seletores conforme HTML real)
                complaint_elements = soup.find_all('div', class_='complain')

                for elem in complaint_elements:
                    try:
                        complaint = self._extract_complaint_data(elem)
                        if complaint:
                            self.complaints.append(complaint)
                    except Exception as e:
                        logger.error(f"Erro ao extrair reclamação: {e}")

                self._random_delay()

        except Exception as e:
            logger.error(f"Erro no scraping: {e}")
        finally:
            driver.quit()

        logger.info(f"Total de reclamações coletadas: {len(self.complaints)}")
        return self.complaints

    def _extract_complaint_data(self, element) -> Dict:
        """Extrair dados de uma reclamação"""
        # NOTA: Ajustar seletores conforme HTML real do Reclame Aqui

        title = element.find('h4')
        text = element.find('p', class_='complain-text')
        date = element.find('span', class_='complain-date')
        user = element.find('span', class_='complain-user')
        status = element.find('span', class_='complain-status')

        return {
            'title': title.text.strip() if title else '',
            'text': text.text.strip() if text else '',
            'date': self._parse_date(date.text.strip() if date else ''),
            'user': user.text.strip() if user else 'Anônimo',
            'status': status.text.strip() if status else 'Não respondida',
            'scraped_at': datetime.now()
        }

    def _parse_date(self, date_str: str) -> datetime:
        """Converter data do formato do Reclame Aqui"""
        # Implementar parsing específico
        # Exemplo: "há 2 dias" -> datetime
        # Por enquanto, retornar data atual
        return datetime.now()
```

3. **Tratamento de erros e retry** (1h):
   - Adicionar try/except em pontos críticos
   - Implementar retry automático (3 tentativas)
   - Logging detalhado de erros
   - Salvar HTML da página em caso de erro (para debug)

4. **Teste do scraper** (1h):
   - Criar script de teste `backend/test_scraper.py`
   - Coletar 50-100 reclamações
   - Validar dados coletados
   - Ajustar seletores se necessário

**Expected Result:**
- ✅ Scraper funcional coletando reclamações
- ✅ Pelo menos 50 reclamações coletadas
- ✅ Dados estruturados corretamente
- ✅ Tratamento de erros implementado
- ✅ Logging detalhado

---

### Task 3: Configurar Database PostgreSQL/SQLite (3h)

**Objective:** Criar estrutura de banco de dados para armazenar reclamações

**Steps:**

1. **Configurar database connection** em `app/core/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

2. **Criar modelo SQLAlchemy** em `app/db/models.py`:

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # Dados do scraping
    title = Column(String(500))
    text = Column(Text, nullable=False)
    user_name = Column(String(200))
    complaint_date = Column(DateTime)
    status = Column(String(100))  # Respondida, Não respondida, Resolvida
    category = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    external_id = Column(String(100), unique=True, nullable=True)  # ID do Reclame Aqui

    # Análise (preenchido por Chat B)
    sentiment = Column(String(50), nullable=True)  # Negativo, Neutro, Positivo
    sentiment_score = Column(Float, nullable=True)  # 0-10
    classification = Column(JSON, nullable=True)  # Array de categorias
    entities = Column(JSON, nullable=True)  # Entidades extraídas
    urgency_score = Column(Float, nullable=True)  # 0-10

    # Resposta (preenchido por Chat C)
    response_generated = Column(Text, nullable=True)
    response_edited = Column(Text, nullable=True)
    coupon_code = Column(String(50), nullable=True)
    coupon_discount = Column(Integer, nullable=True)  # Percentual
    response_sent = Column(Boolean, default=False)
    response_sent_at = Column(DateTime, nullable=True)

    # Metadata
    scraped_at = Column(DateTime, server_default=func.now())
    analyzed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Complaint {self.id}: {self.title[:50]}...>"
```

3. **Criar schemas Pydantic** em `app/schemas/complaint.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ComplaintBase(BaseModel):
    title: str
    text: str
    user_name: str
    complaint_date: Optional[datetime] = None
    status: str = "Não respondida"
    category: Optional[str] = None
    location: Optional[str] = None

class ComplaintCreate(ComplaintBase):
    pass

class Complaint(ComplaintBase):
    id: int
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    urgency_score: Optional[float] = None
    response_generated: Optional[str] = None
    coupon_code: Optional[str] = None
    scraped_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ComplaintStats(BaseModel):
    total: int
    by_sentiment: dict
    by_status: dict
    by_category: dict
    avg_urgency: float
```

4. **Implementar funções CRUD** em `app/db/crud.py`:

```python
from sqlalchemy.orm import Session
from app.db.models import Complaint
from app.schemas.complaint import ComplaintCreate
from typing import List, Optional
from datetime import datetime

def create_complaint(db: Session, complaint: ComplaintCreate) -> Complaint:
    db_complaint = Complaint(**complaint.dict())
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

def get_complaint(db: Session, complaint_id: int) -> Optional[Complaint]:
    return db.query(Complaint).filter(Complaint.id == complaint_id).first()

def get_complaints(db: Session, skip: int = 0, limit: int = 100) -> List[Complaint]:
    return db.query(Complaint).offset(skip).limit(limit).all()

def get_complaints_by_sentiment(db: Session, sentiment: str) -> List[Complaint]:
    return db.query(Complaint).filter(Complaint.sentiment == sentiment).all()

def update_complaint_analysis(db: Session, complaint_id: int, **kwargs):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        for key, value in kwargs.items():
            setattr(complaint, key, value)
        complaint.analyzed_at = datetime.now()
        db.commit()
        db.refresh(complaint)
    return complaint

def bulk_create_complaints(db: Session, complaints: List[dict]):
    db_complaints = [Complaint(**c) for c in complaints]
    db.bulk_save_objects(db_complaints)
    db.commit()
```

5. **Criar e rodar migrations**:

```bash
alembic init migrations
alembic revision --autogenerate -m "Create complaints table"
alembic upgrade head
```

**Expected Result:**
- ✅ Database configurado (PostgreSQL ou SQLite)
- ✅ Modelos SQLAlchemy criados
- ✅ Schemas Pydantic criados
- ✅ Funções CRUD implementadas
- ✅ Migrations rodando

---

### Task 4: Sistema de Polling (2h)

**Objective:** Configurar scraper para rodar automaticamente a cada X horas

**Steps:**

1. **Implementar scheduler** em `app/scraper/scheduler.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.scraper.reclame_aqui_scraper import ReclameAquiScraper
from app.core.database import SessionLocal
from app.db.crud import bulk_create_complaints
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def scrape_job():
    """Job que roda periodicamente"""
    logger.info("Iniciando scraping job...")

    try:
        scraper = ReclameAquiScraper(
            company_url=settings.RECLAME_AQUI_COMPANY_URL,
            max_pages=settings.SCRAPER_MAX_PAGES
        )

        complaints = scraper.scrape_complaints()

        # Salvar no banco
        db = SessionLocal()
        try:
            # Evitar duplicatas: verificar external_id
            new_complaints = []
            for complaint in complaints:
                exists = db.query(Complaint).filter(
                    Complaint.external_id == complaint.get('external_id')
                ).first()
                if not exists:
                    new_complaints.append(complaint)

            if new_complaints:
                bulk_create_complaints(db, new_complaints)
                logger.info(f"Salvos {len(new_complaints)} novas reclamações")
            else:
                logger.info("Nenhuma reclamação nova encontrada")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Erro no scraping job: {e}")

def start_scheduler():
    """Iniciar scheduler"""
    interval_hours = settings.SCRAPER_POLLING_INTERVAL_HOURS

    scheduler.add_job(
        scrape_job,
        'interval',
        hours=interval_hours,
        id='scrape_complaints',
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Scheduler iniciado. Rodará a cada {interval_hours} horas.")

def stop_scheduler():
    scheduler.shutdown()
```

2. **Integrar scheduler no FastAPI**:

```python
# Em app/main.py
from app.scraper.scheduler import start_scheduler, stop_scheduler

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()  # Iniciar scraping automático

@app.on_event("shutdown")
async def shutdown():
    stop_scheduler()
```

3. **Criar endpoint manual** para testar:

```python
@app.post("/scrape/run")
async def run_scraper_manually():
    """Rodar scraper manualmente (para testes)"""
    from app.scraper.scheduler import scrape_job
    scrape_job()
    return {"message": "Scraping iniciado"}
```

**Expected Result:**
- ✅ Scheduler configurado
- ✅ Scraping automático a cada X horas
- ✅ Evita duplicatas
- ✅ Logging de execuções
- ✅ Endpoint manual para testes

---

### Task 5: API Endpoints Básicos (2h)

**Objective:** Criar endpoints REST para acesso aos dados

**Steps:**

1. **Implementar endpoints** em `app/api/endpoints/complaints.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.crud import (
    get_complaint,
    get_complaints,
    get_complaints_by_sentiment,
    create_complaint
)
from app.schemas.complaint import Complaint, ComplaintCreate, ComplaintStats
from app.core.database import get_db
from app.db.models import Complaint as ComplaintModel

router = APIRouter(prefix="/complaints", tags=["complaints"])

@router.get("/", response_model=List[Complaint])
def list_complaints(
    skip: int = 0,
    limit: int = 100,
    sentiment: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar reclamações com filtros opcionais"""
    query = db.query(ComplaintModel)

    if sentiment:
        query = query.filter(ComplaintModel.sentiment == sentiment)
    if status:
        query = query.filter(ComplaintModel.status == status)

    complaints = query.offset(skip).limit(limit).all()
    return complaints

@router.get("/stats", response_model=ComplaintStats)
def get_stats(db: Session = Depends(get_db)):
    """Estatísticas gerais"""
    total = db.query(ComplaintModel).count()

    # Por sentimento
    sentiments = db.query(
        ComplaintModel.sentiment,
        func.count(ComplaintModel.id)
    ).group_by(ComplaintModel.sentiment).all()

    by_sentiment = {s[0]: s[1] for s in sentiments if s[0]}

    # Por status
    statuses = db.query(
        ComplaintModel.status,
        func.count(ComplaintModel.id)
    ).group_by(ComplaintModel.status).all()

    by_status = {s[0]: s[1] for s in statuses if s[0]}

    # Urgência média
    avg_urgency = db.query(func.avg(ComplaintModel.urgency_score)).scalar() or 0

    return ComplaintStats(
        total=total,
        by_sentiment=by_sentiment,
        by_status=by_status,
        by_category={},
        avg_urgency=avg_urgency
    )

@router.get("/{complaint_id}", response_model=Complaint)
def get_complaint_detail(complaint_id: int, db: Session = Depends(get_db)):
    """Detalhe de uma reclamação"""
    complaint = get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Reclamação não encontrada")
    return complaint

@router.post("/", response_model=Complaint)
def create_complaint_endpoint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    """Criar reclamação manualmente (para testes)"""
    return create_complaint(db, complaint)
```

2. **Registrar router** em `app/main.py`:

```python
from app.api.endpoints import complaints

app.include_router(complaints.router)
```

3. **Testar endpoints**:
   - Acessar http://localhost:8000/docs
   - Testar cada endpoint
   - Validar respostas

**Expected Result:**
- ✅ GET /complaints - Lista reclamações
- ✅ GET /complaints/{id} - Detalhe
- ✅ GET /complaints/stats - Estatísticas
- ✅ POST /complaints - Criar (teste)
- ✅ Documentação Swagger funcionando

---

## 📝 Deliverables

Create these files in `coordination/answers/`:

1. **`answer_chat_A_1.md`** - Your results (use template below)
2. **Backend code** - All files mentioned above
3. **README.md** - Instructions to setup and run

**Answer File Must Include:**

- Status (✅ Complete / 🔄 In Progress / ⚠️ Blocked)
- Summary of what was done
- Number of complaints scraped
- Database schema created
- API endpoints implemented
- Issues encountered and solutions
- Time tracking summary
- Next steps recommendation

---

## ⏰ Time Tracking (Mandatory)

**Start your work with:**

```markdown
# Chat A - Round 1 - Time Tracking

**Started:** [HH:MM]
**Estimated Duration:** 12-16 hours
**Expected Completion:** [HH:MM] (Day 2 EOD)
**Timeout Threshold:** [HH:MM] (ETA + 10%)

## Task Breakdown

| Task | Estimated | Actual | Status |
|------|-----------|--------|--------|
| Task 1: Setup | 2h | - | ⏳ |
| Task 2: Scraper | 6h | - | ⏳ |
| Task 3: Database | 3h | - | ⏳ |
| Task 4: Polling | 2h | - | ⏳ |
| Task 5: API | 2h | - | ⏳ |
```

**Update progress every 15 minutes during active work**

**Post checkpoint updates at:**
- 25% complete (after Task 1)
- 50% complete (after Task 2) - **CRITICAL: Chat B will start here**
- 75% complete (after Task 4)
- 100% complete

**If you hit timeout threshold (ETA + 10%), STOP and create timeout alert**

---

## 🎯 Success Criteria

- ✅ Backend structure created following best practices
- ✅ Scraper collected at least 50 real complaints from Reclame Aqui
- ✅ Database configured with proper schema
- ✅ Data stored correctly without duplicates
- ✅ API endpoints working and documented
- ✅ Polling system configured
- ✅ Code is clean, documented, and follows PEP 8
- ✅ README with clear setup instructions

---

## 📞 Questions?

If you encounter:

- **Reclame Aqui HTML changed** → Document the new structure, try alternative selectors, create `question_A_to_commander_1.md` if blocked
- **Selenium/ChromeDriver issues** → Try headless mode, check driver version, document error
- **Database connection errors** → Check `.env` config, try SQLite first, then PostgreSQL
- **Too few complaints scraped** → Increase `max_pages`, check filters, verify selectors
- **Rate limiting from Reclame Aqui** → Increase delays, rotate user agents, document issue
- **Anything else** → Create `question_A_to_commander_N.md`

**Important Notes:**

1. **Prioritize getting data first** - Even if selectors are imperfect, collect what you can. We can refine later.
2. **Use SQLite for MVP** - Faster to setup. PostgreSQL can wait for production.
3. **Start with 2-3 pages** - Test thoroughly before scaling to max_pages.
4. **Document HTML structure** - Will help other chats understand data.
5. **At 50% completion**, notify Commander - Chat B depends on you!

---

## 🔄 Related Tasks

- **Chat B** (AI Analysis) will use your data starting at your 50% completion
- **Chat D** (Frontend) needs your API endpoints working
- **Chat E** (Docs) will document your API

**Your output is CRITICAL - everyone depends on you! 🚀**

---

## 📊 Checkpoint Reporting

**At 50% (CRITICAL):**

Create file `coordination/alerts/checkpoint_A_50.md`:

```markdown
# ✅ Chat A - 50% Checkpoint

**Date:** [Date/Time]
**Status:** On Track / Delayed

## Completed
- [ ] Task 1: Setup
- [ ] Task 2: Scraper

## Database Status
- Complaints collected: [N]
- Database: ✅ Working / ⚠️ Issues

## API Status
- Endpoints: ✅ Ready / 🔄 In Progress

## Blockers
- None / [List issues]

## Ready for Chat B?
- ✅ Yes - Data available / ⚠️ Not yet

**Commander Action:** Chat B can start / Wait
```

---

**Start when ready! Good luck! 🚀**

**Remember:** You are the foundation. Take your time to do it right, but stay on schedule. The entire project depends on your success!

**Questions or blockers?** → Don't wait! Create alert/question file immediately.

**Commander is monitoring** - Updates every 2 hours expected.
