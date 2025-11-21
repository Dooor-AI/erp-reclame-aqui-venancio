# 🤖 RPA de Reembolsos Venâncio

Sistema automatizado de monitoramento e resposta para reclamações no Reclame Aqui.

![Status](https://img.shields.io/badge/status-planejamento%20completo-green)
![Timeline](https://img.shields.io/badge/timeline-5%20dias-blue)
![Progress](https://img.shields.io/badge/progress-0%25-orange)

---

## 📋 Visão Geral

MVP funcional que automatiza a gestão de reclamações da Venâncio no Reclame Aqui:

- 🔍 **Monitoramento 24/7** - Coleta automática de reclamações
- 🧠 **Análise com IA** - Sentimento, classificação e urgência
- ✍️ **Respostas Personalizadas** - Geradas por Claude AI
- 🎁 **Cupons Automáticos** - Compensação inteligente
- 📊 **Dashboard CRM** - Gestão visual de reclamações

### Problema
A Venâncio tem score baixo em plataformas de reclamação devido a falta de respostas adequadas, impactando a imagem da marca.

### Solução
Sistema que monitora, analisa e responde automaticamente, melhorando tempo de resposta e satisfação do cliente.

---

## 🎯 Métricas de Sucesso

- ✅ **50+ reclamações coletadas** automaticamente
- ✅ **80%+ acurácia** na análise de sentimento
- ✅ **100% respostas coerentes** e empáticas
- ✅ **Dashboard funcional** e profissional
- ✅ **Documentação completa** para handoff

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│  Reclame Aqui   │
└────────┬────────┘
         │ Scraping (Selenium)
    ┌────▼─────┐
    │ Backend  │
    │ Python   │ ──► Claude API (IA)
    │ FastAPI  │
    └────┬─────┘
         │ REST API
    ┌────▼─────┐
    │ Frontend │
    │ Next.js  │
    │Dashboard │
    └──────────┘
```

### Stack Tecnológica

**Backend:**
- Python 3.11+ + FastAPI
- PostgreSQL / SQLite
- Anthropic Claude API
- BeautifulSoup4 + Selenium
- SQLAlchemy

**Frontend:**
- Next.js 15 + React 19
- TypeScript 5
- Tailwind CSS v4 + Shadcn/ui
- TanStack React Query
- Recharts

**Referência de Design:**
- Baseado no UX/UI do veris-frontend (ver [REFERENCIA_DESIGN.md](REFERENCIA_DESIGN.md))

---

## 🚀 Quick Start

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- PostgreSQL (ou SQLite para MVP)
- API Key do Anthropic Claude

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Configure ANTHROPIC_API_KEY no .env

uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs (Swagger UI)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:3000

---

## 📂 Estrutura do Projeto

```
projeto_venancio/
├── coordination/              # Sistema de coordenação Multi-AI
│   ├── COMMAND_CENTER.md     # Status tracker
│   ├── TASK_ASSIGNMENTS.md   # Distribuição de tarefas
│   ├── orders/               # Ordens para cada Chat
│   ├── answers/              # Respostas dos Chats
│   └── logs/                 # Logs diários
│
├── backend/                  # Backend Python + FastAPI
│   ├── app/
│   │   ├── api/             # Endpoints REST
│   │   ├── core/            # Config e database
│   │   ├── db/              # Models SQLAlchemy
│   │   ├── scraper/         # Web scraping
│   │   ├── ai/              # IA (Claude)
│   │   ├── services/        # Business logic
│   │   └── schemas/         # Pydantic schemas
│   └── tests/               # Testes
│
├── frontend/                # Frontend Next.js
│   ├── app/                # App Router
│   ├── components/         # Componentes React
│   ├── lib/                # API client
│   ├── hooks/              # Hooks customizados
│   └── store/              # Zustand state
│
└── docs/                    # Documentação
    ├── ARCHITECTURE.md     # Arquitetura detalhada
    ├── API.md              # API reference
    └── DEPLOYMENT.md       # Guia de deploy
```

---

## 📊 Funcionalidades

### MVP (Semana 1)
- ✅ Coleta automática de reclamações (Reclame Aqui)
- ✅ Análise de sentimento com IA
- ✅ Classificação automática por tipo
- ✅ Geração de respostas personalizadas
- ✅ Sistema de cupons de desconto
- ✅ Dashboard com estatísticas

### Próximas Fases
- 🔜 Integração com API oficial Reclame Aqui
- 🔜 Postagem automática de respostas
- 🔜 Expansão para Google Reviews
- 🔜 Expansão para Instagram
- 🔜 Sistema de aprovação humana (HITL)
- 🔜 Detecção de fraude
- 🔜 Relatórios gerenciais

---

## 👥 Metodologia de Desenvolvimento

Este projeto utiliza o **Sistema de Coordenação Multi-AI** com 4 chats otimizados:

| Chat | Especialização | Duração | Status |
|------|----------------|---------|--------|
| **A** | Backend Foundation (Scraping + DB + API) | 12-14h | ⏳ Pending |
| **B** | Backend Intelligence (AI + Responses) | 10-12h | ⏳ Pending |
| **C** | Frontend Complete (Dashboard + UI) | 10-12h | ⏳ Pending |
| **D** | Integration & Documentation | 8-10h | ⏳ Pending |

**Acompanhe o progresso em:** [coordination/COMMAND_CENTER.md](coordination/COMMAND_CENTER.md)

---

## 📅 Cronograma

| Dia | Data | Tarefas |
|-----|------|---------|
| 1 | 17 Nov | Chat A: Backend Foundation |
| 2 | 18 Nov | Chat A completa + Chat B & C iniciam |
| 3 | 19 Nov | Chat B: Response Generator + Chat C: Dashboard |
| 4 | 20 Nov | Chat B & C completam + Chat D: Integration |
| 5 | 21-22 Nov | Chat D: Docs + Demo Final ✅ |

---

## 📚 Documentação

### Documentos de Planejamento
- [📊 Resumo Executivo](RESUMO_EXECUTIVO_PLANEJAMENTO.md) - Visão geral completa
- [🎯 Command Center](coordination/COMMAND_CENTER.md) - Status em tempo real
- [📋 Task Assignments](coordination/TASK_ASSIGNMENTS.md) - Distribuição de tarefas

### Documentação Técnica (será criada)
- [🏗️ Arquitetura](docs/ARCHITECTURE.md) - Diagramas e explicações
- [📡 API Reference](docs/API.md) - Endpoints e exemplos
- [🚀 Deployment](docs/DEPLOYMENT.md) - Guia de deploy

### Ordens de Trabalho (4 Chats)
- [Chat A - Backend Foundation](coordination/orders/order_chat_A_1.md)
- [Chat B - Backend Intelligence](coordination/orders/order_chat_B_1.md)
- [Chat C - Frontend Complete](coordination/orders/order_chat_C_1.md)
- [Chat D - Integration & Docs](coordination/orders/order_chat_D_1.md)

---

## 🧪 Testes

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm test
```

---

## 🐳 Docker (Opcional)

```bash
docker-compose up -d
```

Serviços:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

---

## 🔐 Segurança

- API keys em variáveis de ambiente (`.env`)
- CORS configurado
- Rate limiting no scraper
- Validação de dados com Pydantic
- Sanitização de inputs

---

## 📈 Roadmap

### Fase 1: MVP (Semana 1) ✅ Em Andamento
- Scraping + Database
- Análise com IA
- Geração de respostas
- Dashboard básico

### Fase 2: Automação (Semanas 2-3)
- Postagem automática
- Integração com sistema real de cupons
- API oficial Reclame Aqui

### Fase 3: Expansão (Semanas 4-5)
- Google Reviews
- Instagram
- Sistema HITL (Human-in-the-Loop)

### Fase 4: Analytics (Mês 2)
- Dashboard avançado
- Detecção de fraude
- Relatórios gerenciais
- BI integrado

---

## 💡 ROI Estimado

**Antes do RPA:**
- ⏱️ Tempo de resposta: 48-72h
- 📊 Taxa de resposta: 40%
- ⭐ Score Reclame Aqui: 6.2
- 👤 Tempo manual: ~2000h/ano

**Projeção com RPA:**
- ⚡ Tempo de resposta: <4h
- 📈 Taxa de resposta: 90%+
- 🌟 Score projetado: 8.0+
- 🤖 Automação: 85%+

**Economia anual:** ~2000h de atendimento manual
**Melhoria de imagem:** Priceless 😊

---

## 🤝 Contribuindo

Este é um projeto piloto MVP. Contribuições são bem-vindas após a validação inicial.

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

[Definir licença]

---

## 📞 Contato

**Projeto:** RPA de Reembolsos Venâncio
**Cliente:** Venâncio
**Desenvolvedor:** DOOOR AI Team
**Período:** 17-22 Nov 2025

---

## 🎓 Referências

- [Template de Coordenação Multi-AI](PARALLEL_AI_COORDINATION_TEMPLATE.md)
- [Referência de Design Frontend](REFERENCIA_DESIGN.md)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Next.js 15 Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

**Status:** 🟢 Planejamento Completo - Pronto para Execução
**Última Atualização:** 2025-11-17
**Próxima Ação:** 🚀 Iniciar Chat A (Scraping + Database)

---

<div align="center">

**🤖 Automatizando o atendimento, humanizando a resposta. 🤖**

</div>
