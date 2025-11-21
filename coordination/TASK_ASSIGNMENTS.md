# 📋 Task Assignments - RPA de Reembolsos Venâncio

**Projeto:** Sistema de Monitoramento e Resposta Automática para Reclame Aqui
**Data:** 2025-11-17
**Status:** Planejamento concluído, pronto para execução

---

## 🎯 Visão Geral das Atribuições

### Estratégia de Paralelização

O projeto está dividido em **5 chats paralelos**, cada um com foco em uma especialização:

1. **Chat A** - Backend: Scraping & Database (Foundation)
2. **Chat B** - Backend: AI & Classification (Intelligence)
3. **Chat C** - Backend: Response Generator (Automation)
4. **Chat D** - Frontend: Dashboard (Interface)
5. **Chat E** - Documentation & QA (Quality)

### Princípios de Divisão
- ✅ Tarefas independentes sempre que possível
- ✅ Dependências claras e documentadas
- ✅ Cada chat tem foco único (sem sobreposição)
- ✅ Estimativas de tempo realistas com buffer de 10%
- ✅ Checkpoints de integração definidos

---

## 📊 Chat A - Backend: Scraping & Database

### Responsabilidade
Criar a fundação de dados do sistema: coletar reclamações do Reclame Aqui e armazená-las em banco estruturado.

### Prioridade
🔴 **Critical** - Todos os outros chats dependem dos dados coletados

### Duração Estimada
**12-16 horas** (Dias 1-2)

### Tarefas Detalhadas

#### Task 1: Setup do Projeto Backend (2h)
- Criar estrutura de pastas do backend Python
- Configurar ambiente virtual
- Instalar dependências (BeautifulSoup4, Selenium, Requests, FastAPI, SQLAlchemy, etc.)
- Criar arquivo de configuração (.env)
- Setup inicial do FastAPI

#### Task 2: Implementar Scraper do Reclame Aqui (6h)
- Analisar estrutura HTML do Reclame Aqui (perfil Venâncio)
- Implementar scraper com BeautifulSoup/Selenium
- Coletar: texto da reclamação, data, usuário, status, categoria
- Implementar delays e user agents rotativos (anti-scraping)
- Tratamento de erros e retry logic
- Logging detalhado
- Coletar 50-100 reclamações históricas

#### Task 3: Configurar Database PostgreSQL/SQLite (3h)
- Criar modelos SQLAlchemy para reclamações
- Definir schema do banco:
  - Tabela: complaints (id, texto, data, usuario, status, categoria, sentimento, urgencia, resposta_gerada, etc.)
- Implementar migrations (Alembic)
- Criar funções CRUD básicas
- Popular banco com dados coletados

#### Task 4: Sistema de Polling (2h)
- Implementar scheduler para rodar scraper periodicamente
- Configurar intervalo (a cada X horas - configurável)
- Detectar novas reclamações (evitar duplicatas)
- Logging de execuções

#### Task 5: API Endpoints Básicos (2h)
- GET /complaints - Listar reclamações
- GET /complaints/{id} - Detalhe de reclamação
- GET /complaints/stats - Estatísticas básicas
- Documentação automática com FastAPI (Swagger)

### Dependências
**Nenhuma** - Pode começar imediatamente

### Entregáveis
1. ✅ Backend funcional com FastAPI
2. ✅ Database com 50-100 reclamações reais
3. ✅ Script de scraping rodando em background
4. ✅ API REST documentada
5. ✅ README com instruções de setup

### Success Criteria
- [ ] Sistema coletou pelo menos 50 reclamações
- [ ] Database estruturado e populado
- [ ] API retorna dados corretamente
- [ ] Scraper roda sem erros
- [ ] Código documentado e organizado

### Arquivos a Criar
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── db/
│   │   ├── models.py
│   │   └── base.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── reclame_aqui_scraper.py
│   │   └── scheduler.py
│   ├── api/
│   │   └── endpoints/
│   │       └── complaints.py
│   └── schemas/
│       └── complaint.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📊 Chat B - Backend: AI & Classification

### Responsabilidade
Implementar análise de sentimento e classificação automática de reclamações usando LLMs.

### Prioridade
🔴 **Critical** - Necessário para gerar respostas inteligentes

### Duração Estimada
**8-10 horas** (Dias 2-3)

### Tarefas Detalhadas

#### Task 1: Integração com API Claude (2h)
- Configurar Anthropic Claude API
- Criar wrapper para chamadas à API
- Implementar retry logic e rate limiting
- Tratamento de erros da API
- Sistema de cache (evitar chamadas duplicadas)

#### Task 2: Análise de Sentimento (2h)
- Criar prompt para análise de sentimento
- Classificar em: Negativo / Neutro / Positivo
- Extrair score de 0-10
- Validar com amostra manual (80%+ acurácia)
- Armazenar resultado no banco

#### Task 3: Classificação de Tipo de Reclamação (2h)
- Criar prompt para classificação
- Categorias: produto, atendimento, entrega, preço, outros
- Permitir múltiplas categorias por reclamação
- Armazenar no banco

#### Task 4: Extração de Entidades (2h)
- Extrair: produto mencionado, loja, funcionário
- Usar Named Entity Recognition (NER)
- Estruturar dados extraídos
- Armazenar metadados no banco

#### Task 5: Score de Urgência (1h)
- Calcular score 0-10 baseado em:
  - Sentimento negativo
  - Palavras-chave (processual, judicial, Procon, etc.)
  - Tempo sem resposta
- Priorizar reclamações urgentes

#### Task 6: Dashboard de Estatísticas (1h)
- Endpoint: GET /analytics/sentiment
- Endpoint: GET /analytics/categories
- Endpoint: GET /analytics/urgency
- Gerar insights para o frontend

### Dependências
- **Chat A** deve estar em **50%** (dados disponíveis para testar)
- Acesso à API do Claude (verificar créditos)

### Entregáveis
1. ✅ Sistema de análise de sentimento funcionando
2. ✅ Classificação automática por categoria
3. ✅ Extração de entidades principais
4. ✅ Score de urgência calculado
5. ✅ Endpoints de analytics criados
6. ✅ Validação manual de 80%+ acurácia

### Success Criteria
- [ ] 100% das reclamações analisadas automaticamente
- [ ] Acurácia de sentimento >= 80% (validação manual)
- [ ] Categorias fazem sentido (validação manual)
- [ ] Score de urgência funcional
- [ ] API retorna estatísticas corretas

### Arquivos a Criar
```
backend/app/
├── ai/
│   ├── __init__.py
│   ├── claude_client.py
│   ├── sentiment_analyzer.py
│   ├── classifier.py
│   ├── entity_extractor.py
│   ├── urgency_scorer.py
│   └── prompts/
│       ├── sentiment.txt
│       ├── classification.txt
│       └── entities.txt
└── api/endpoints/
    └── analytics.py
```

---

## 📊 Chat C - Backend: Response Generator

### Responsabilidade
Criar sistema de geração de respostas automáticas personalizadas e cupons de desconto.

### Prioridade
🟠 **High** - Core do valor do sistema

### Duração Estimada
**6-8 horas** (Dias 3-4)

### Tarefas Detalhadas

#### Task 1: Templates de Resposta (2h)
- Criar templates por categoria:
  - Produto defeituoso
  - Atraso na entrega
  - Problema de atendimento
  - Preço/cobrança incorreta
  - Outros
- Tom empático e profissional
- Estrutura: reconhecimento → desculpa → solução → cupom

#### Task 2: Gerador com LLM (3h)
- Criar prompt para personalização
- Usar contexto da reclamação
- Manter tom empático
- Incluir detalhes específicos mencionados
- Validar qualidade da resposta
- Evitar respostas genéricas

#### Task 3: Sistema de Cupons (2h)
- Gerar códigos únicos
- Configurar desconto (10-20% baseado em urgência)
- Validade configurável
- Armazenar cupons no banco
- Evitar duplicatas

#### Task 4: API de Respostas (1h)
- POST /responses/generate - Gerar resposta para reclamação
- GET /responses/{complaint_id} - Ver resposta gerada
- PUT /responses/{id} - Editar resposta (antes de enviar)
- Documentação

### Dependências
- **Chat B** deve estar **100%** completo (análise e classificação funcionando)
- **Chat A** deve ter API funcionando

### Entregáveis
1. ✅ Templates de resposta por categoria
2. ✅ Sistema de personalização com LLM
3. ✅ Gerador de cupons únicos
4. ✅ API de respostas criada
5. ✅ 10-15 exemplos de respostas geradas validadas

### Success Criteria
- [ ] 100% das respostas são coerentes e empáticas
- [ ] Personalização funciona (não genérico)
- [ ] Cupons únicos e rastreáveis
- [ ] API funcional
- [ ] Validação manual de qualidade

### Arquivos a Criar
```
backend/app/
├── ai/
│   ├── response_generator.py
│   └── prompts/
│       └── response.txt
├── services/
│   ├── coupon_service.py
│   └── response_service.py
├── db/models.py (adicionar Response e Coupon)
└── api/endpoints/
    └── responses.py
```

---

## 📊 Chat D - Frontend: Dashboard

### Responsabilidade
Criar interface web para visualização de reclamações, estatísticas e geração de respostas.

### Prioridade
🟠 **High** - Interface para demonstração

### Duração Estimada
**10-12 horas** (Dias 2-5, paralelo aos outros)

### Tarefas Detalhadas

#### Task 1: Setup do Projeto Frontend (2h)
**Início:** Dia 2 (quando Chat A tiver API básica)
- Criar projeto Next.js 15 + TypeScript
- Configurar Tailwind CSS v4
- Instalar Shadcn/ui
- Configurar Zustand
- Configurar TanStack React Query
- Setup de estrutura de pastas (padrão veris-frontend)

#### Task 2: Componentes Base (2h)
- Layout principal com sidebar
- Header com logo e navegação
- Sidebar com menu
- Card component para reclamações
- Badge para status/sentimento
- Loading states e skeletons

#### Task 3: Página de Reclamações (3h)
- Lista de reclamações (table ou cards)
- Filtros: sentimento, categoria, urgência, status
- Ordenação: data, urgência
- Paginação
- Detalhamento ao clicar (modal ou página)
- Indicador visual de urgência

#### Task 4: Dashboard de Estatísticas (2h)
- Gráficos com Recharts:
  - Volume de reclamações por dia (line chart)
  - Distribuição de sentimentos (pie chart)
  - Top 5 categorias (bar chart)
- Cards com KPIs:
  - Total de reclamações
  - Taxa de resposta
  - Tempo médio de resposta
  - Reclamações urgentes

#### Task 5: Gerador de Respostas (2h)
- Botão "Gerar Resposta" em cada reclamação
- Modal com resposta sugerida
- Editor para modificar resposta
- Preview do cupom gerado
- Botão "Enviar" (mock - apenas salva no banco)
- Feedback visual (toast/notification)

#### Task 6: Integração com Backend (1h)
- Configurar API client
- Conectar com endpoints do backend
- Error handling
- Loading states
- Refresh automático de dados

### Dependências
- **Chat A** deve estar em **30%** (API básica funcionando)
- **Chat B** deve estar em **50%** (para dashboard de estatísticas)
- **Chat C** deve estar **completo** (para gerador de respostas)

### Entregáveis
1. ✅ Interface web funcional
2. ✅ Dashboard com estatísticas em tempo real
3. ✅ Visualização de reclamações com filtros
4. ✅ Gerador de respostas integrado
5. ✅ Design responsivo e profissional

### Success Criteria
- [ ] Dashboard carrega dados do backend
- [ ] Filtros e ordenação funcionam
- [ ] Gráficos exibem dados corretos
- [ ] Gerador de respostas funcional
- [ ] Interface intuitiva e responsiva

### Arquivos a Criar
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx (dashboard)
│   │   └── reclamacoes/
│   │       ├── page.tsx
│   │       └── [id]/page.tsx
│   ├── components/
│   │   ├── ui/ (Shadcn/ui)
│   │   ├── dashboard/
│   │   │   ├── stats-card.tsx
│   │   │   ├── sentiment-chart.tsx
│   │   │   └── category-chart.tsx
│   │   ├── reclamacoes/
│   │   │   ├── reclamacao-card.tsx
│   │   │   ├── reclamacao-table.tsx
│   │   │   └── filters.tsx
│   │   └── respostas/
│   │       ├── response-generator.tsx
│   │       └── response-editor.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── use-complaints.ts
│   │   └── use-analytics.ts
│   ├── store/
│   │   └── appStore.ts
│   └── types/
│       └── complaint.ts
└── package.json
```

---

## 📊 Chat E - Documentation & QA

### Responsabilidade
Documentação técnica, testes, preparação de apresentação e suporte ao deploy.

### Prioridade
🟡 **Medium** - Suporte e qualidade

### Duração Estimada
**8-10 horas** (Dias 3-5, paralelo aos outros)

### Tarefas Detalhadas

#### Task 1: Documentação Técnica (4h)
**Início:** Dia 3 (quando arquitetura estiver definida)
- README.md principal do projeto
- ARCHITECTURE.md - Diagrama e explicação
- API.md - Documentação de todos os endpoints
- DEPLOYMENT.md - Guia de deploy
- Instruções de setup para desenvolvimento
- Troubleshooting guide

#### Task 2: Testes Automatizados (3h)
- Testes unitários do scraper (mocks)
- Testes de integração da API
- Validação de respostas geradas (amostra)
- Testes do frontend (componentes críticos)
- Script de teste end-to-end

#### Task 3: Preparação de Apresentação (2h)
- Slides/documento explicativo do projeto
- Screenshots do dashboard
- Exemplos de respostas geradas
- Métricas de sucesso atingidas
- Roadmap para próximos passos

#### Task 4: Docker Setup (Opcional) (1h)
- Dockerfile para backend
- Dockerfile para frontend
- docker-compose.yml
- Instruções de uso

### Dependências
- **Todos os chats** devem estar em **80%+** para documentar completamente

### Entregáveis
1. ✅ Documentação técnica completa
2. ✅ Testes automatizados rodando
3. ✅ Apresentação preparada
4. ✅ Guia de deploy funcional
5. ✅ Docker setup (opcional)

### Success Criteria
- [ ] Qualquer desenvolvedor consegue rodar o projeto
- [ ] Documentação clara e completa
- [ ] Testes cobrem casos críticos
- [ ] Apresentação profissional
- [ ] Deploy documentado

### Arquivos a Criar
```
docs/
├── ARCHITECTURE.md
├── API.md
└── DEPLOYMENT.md

backend/
├── tests/
│   ├── test_scraper.py
│   ├── test_api.py
│   └── test_ai.py

frontend/
├── tests/
│   └── components/

├── Dockerfile (backend)
├── Dockerfile (frontend)
├── docker-compose.yml
└── README.md
```

---

## 🔄 Cronograma de Integração

### Dia 1 (17 Nov)
- **09:00** - Chat A inicia (Scraping + DB)
- **17:00** - Chat A checkpoint 50% (dados disponíveis)

### Dia 2 (18 Nov)
- **09:00** - Chat B inicia (AI Analysis)
- **09:00** - Chat D inicia Task 1 (Frontend Setup)
- **17:00** - Chat A completa (100%)
- **17:00** - Chat B checkpoint 50%

### Dia 3 (19 Nov)
- **09:00** - Chat B completa (100%)
- **09:00** - Chat C inicia (Response Generator)
- **09:00** - Chat E inicia Task 1 (Documentação)
- **14:00** - Chat D Task 3-4 (Dashboard stats)

### Dia 4 (20 Nov)
- **09:00** - Chat C completa (100%)
- **09:00** - Chat D Task 5 (Gerador de respostas)
- **14:00** - Chat E Task 2 (Testes)

### Dia 5 (21-22 Nov)
- **09:00** - Integração final
- **12:00** - Chat D completa (100%)
- **14:00** - Chat E completa (100%)
- **16:00** - Demo final preparada

---

## 📊 Matriz de Responsabilidades (RACI)

| Task | Chat A | Chat B | Chat C | Chat D | Chat E | Commander |
|------|--------|--------|--------|--------|--------|-----------|
| Scraping | R,A | I | - | I | C | A |
| Database | R,A | C | C | I | I | A |
| AI Analysis | I | R,A | C | I | C | A |
| Classification | I | R,A | C | I | C | A |
| Response Gen | - | C | R,A | I | C | A |
| Frontend | I | I | I | R,A | C | A |
| Docs | C | C | C | C | R,A | A |
| Testing | C | C | C | C | R,A | A |

**Legenda:**
- **R** - Responsible (executa)
- **A** - Accountable (responsável final)
- **C** - Consulted (consultado)
- **I** - Informed (informado)

---

## 🚨 Protocolo de Comunicação

### Para Bloqueadores
1. Criar `alert_[CHAT]_blocked.md` em `coordination/alerts/`
2. Notificar Commander imediatamente
3. Sugerir soluções alternativas
4. Aguardar resposta (max 30 min)

### Para Perguntas Inter-Chat
1. Criar `question_[FROM]_to_[TO]_N.md` em `coordination/questions/`
2. Chat destinatário responde em `answer_[TO]_to_[FROM]_N.md`
3. Prazo de resposta: max 1 hora

### Para Updates de Progresso
1. Atualizar a cada 15 minutos (in-task)
2. Criar checkpoint report a cada 2 horas
3. Notificar Commander em marcos importantes (25%, 50%, 75%, 100%)

### Timeout Protocol
- Se task ultrapassar ETA + 10%, criar timeout alert
- Reavaliar abordagem
- Commander pode realocar task

---

## 📈 KPIs de Sucesso

### Por Chat
- **On-time delivery:** >= 90%
- **Estimation accuracy:** >= 85%
- **Code quality:** Review sem issues críticos
- **Documentation:** Completa e clara

### Projeto Geral
- **Timeline:** Concluir em 5 dias
- **Integração:** 100% funcional
- **Quality:** 80%+ acurácia na análise
- **Demo:** Apresentável ao cliente

---

**Prepared by:** Commander
**Date:** 2025-11-17
**Version:** 1.0
**Status:** Ready for execution
