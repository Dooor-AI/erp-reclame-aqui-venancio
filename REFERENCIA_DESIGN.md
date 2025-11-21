# 🎨 Referência de Design - Frontend

**Fonte:** [veris-frontend](https://github.com/Dooor-AI/veris-frontend) (removido do repo para economizar espaço)

---

## 📋 Stack a Replicar

### Core
- **Next.js 15** com App Router (não Pages Router)
- **React 19** + **TypeScript 5**
- **Tailwind CSS v4** (PostCSS)

### UI Components
- **Shadcn/ui** - Componentes baseados em Radix UI
  - Instalar com: `npx shadcn-ui@latest init`
  - Componentes necessários: button, card, table, badge, dialog, select, input, textarea, toast, tabs

### Estado e Data
- **Zustand** - Estado global
- **TanStack React Query** - Data fetching e cache

### Visualização
- **Recharts** - Gráficos (pie, bar, line)
- **Lucide React** - Ícones

### Utilities
- **clsx** + **tailwind-merge** - Class utilities
- **date-fns** - Formatação de datas
- **sonner** - Toast notifications

---

## 🏗️ Estrutura de Pastas Recomendada

```
frontend/
├── app/
│   ├── layout.tsx              # Layout raiz com providers
│   ├── page.tsx                # Dashboard (/)
│   └── reclamacoes/
│       └── page.tsx            # Lista de reclamações
│
├── components/
│   ├── ui/                     # Shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   ├── badge.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   │
│   ├── layout/
│   │   └── header.tsx          # Header principal
│   │
│   ├── dashboard/
│   │   ├── stats-card.tsx      # Card de KPI
│   │   ├── sentiment-chart.tsx # Gráfico de sentimento
│   │   └── category-chart.tsx  # Gráfico de categorias
│   │
│   ├── reclamacoes/
│   │   ├── reclamacao-card.tsx # Card de reclamação
│   │   ├── reclamacao-table.tsx# Tabela de reclamações
│   │   └── filters.tsx         # Filtros
│   │
│   └── respostas/
│       └── response-generator-dialog.tsx # Modal gerador
│
├── lib/
│   ├── api.ts                  # API client
│   ├── utils.ts                # Utility functions
│   └── types.ts                # TypeScript types
│
├── hooks/
│   ├── use-complaints.ts       # Hook de reclamações
│   └── use-analytics.ts        # Hook de analytics
│
├── store/
│   └── appStore.ts             # Zustand store
│
└── package.json
```

---

## 🎨 Padrões de Design

### 1. Cores e Tema

Usar variáveis CSS no `globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --muted: 210 40% 96.1%;
    --destructive: 0 84.2% 60.2%;
    --border: 214.3 31.8% 91.4%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... */
  }
}
```

### 2. Componentes Base

**StatsCard (KPI):**
```typescript
interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  trend?: 'up' | 'down';
}
```

**ReclamacaoCard:**
```typescript
interface ReclamacaoCardProps {
  complaint: Complaint;
  onGenerateResponse: () => void;
}
```

**SentimentBadge:**
- Negativo: Badge vermelho (destructive)
- Neutro: Badge cinza (secondary)
- Positivo: Badge verde (default)

**UrgencyIndicator:**
- 0-3: Verde
- 4-6: Amarelo
- 7-10: Vermelho

### 3. Gráficos

**Sentiment Chart (Pie):**
```typescript
<PieChart width={400} height={300}>
  <Pie data={sentimentData} dataKey="value" nameKey="name" />
  <Tooltip />
  <Legend />
</PieChart>
```

**Category Chart (Bar):**
```typescript
<BarChart data={categoryData}>
  <XAxis dataKey="name" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="count" fill="#8884d8" />
</BarChart>
```

---

## 🔧 Setup Rápido

### 1. Criar Projeto

```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
```

### 2. Instalar Dependências

```bash
# UI e Estado
npm install @tanstack/react-query zustand
npm install recharts lucide-react
npm install clsx tailwind-merge class-variance-authority
npm install sonner date-fns

# Shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card table badge dialog select input textarea toast tabs
```

### 3. Configurar API Client

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
  return res.json();
}
```

### 4. Criar Query Provider

```typescript
// components/query-provider.tsx
'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: { staleTime: 60_000, retry: 1 },
    },
  }));

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

---

## 🎯 Componentes Essenciais

### Dashboard (Página Principal)

**Elementos:**
1. Header com título "RPA Venâncio"
2. Grid de 4 KPI cards:
   - Total de Reclamações
   - Reclamações Negativas
   - Urgência Média
   - Taxa de Resposta
3. 2 gráficos lado a lado:
   - Pie chart de sentimentos
   - Bar chart de categorias

### Página de Reclamações

**Elementos:**
1. Header com filtros (sentimento, status)
2. Grid de cards de reclamações ou tabela
3. Cada card mostra:
   - Título
   - Trecho do texto
   - Badge de sentimento
   - Badge de urgência
   - Botão "Gerar Resposta"

### Modal de Geração de Resposta

**Elementos:**
1. Botão "Gerar Resposta com IA"
2. Área de texto com resposta gerada (editável)
3. Card com cupom gerado (código + desconto)
4. Botões: "Editar" e "Enviar"

---

## 📱 Design Responsivo

```typescript
// Breakpoints Tailwind
sm: '640px'   // Tablet pequeno
md: '768px'   // Tablet
lg: '1024px'  // Desktop pequeno
xl: '1280px'  // Desktop
2xl: '1536px' // Desktop grande

// Exemplo de uso
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* KPI Cards */}
</div>
```

---

## 🎨 Paleta de Cores Sugerida

```
Primary: #1a1a1a (Preto suave)
Secondary: #6b7280 (Cinza)
Success: #10b981 (Verde)
Warning: #f59e0b (Amarelo)
Danger: #ef4444 (Vermelho)
Background: #ffffff (Branco)
Muted: #f3f4f6 (Cinza claro)
```

---

## 📊 Mockups de Referência

### Dashboard
```
┌─────────────────────────────────────────────┐
│  RPA Venâncio                    [Nav]      │
├─────────────────────────────────────────────┤
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ 152  │ │  89  │ │ 7.2  │ │ 85%  │       │
│  │Total │ │ Neg  │ │Urgên.│ │Resp. │       │
│  └──────┘ └──────┘ └──────┘ └──────┘       │
│                                              │
│  ┌──────────────────┐ ┌─────────────────┐  │
│  │   Pie Chart      │ │   Bar Chart     │  │
│  │   Sentimentos    │ │   Categorias    │  │
│  └──────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────┘
```

### Lista de Reclamações
```
┌─────────────────────────────────────────────┐
│  Reclamações          [Filtros: ▼]          │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │ Produto com defeito    [Negativo]   │   │
│  │ Comprei e chegou quebrado...        │   │
│  │ João Silva - há 2 dias  [Urgên: 8]  │   │
│  │              [Gerar Resposta]       │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ Entrega atrasada       [Negativo]   │   │
│  │ ...                                 │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🔗 Links Úteis

- **Shadcn/ui:** https://ui.shadcn.com/
- **Tailwind CSS:** https://tailwindcss.com/
- **Recharts:** https://recharts.org/
- **TanStack Query:** https://tanstack.com/query
- **Zustand:** https://zustand-demo.pmnd.rs/

---

## ✅ Checklist de Implementação

### Setup
- [ ] Criar projeto Next.js 15
- [ ] Instalar dependências
- [ ] Configurar Shadcn/ui
- [ ] Configurar Tailwind CSS
- [ ] Criar API client

### Componentes
- [ ] Layout principal
- [ ] Header
- [ ] StatsCard
- [ ] SentimentChart
- [ ] CategoryChart
- [ ] ReclamacaoCard
- [ ] ResponseGeneratorDialog

### Páginas
- [ ] Dashboard (/)
- [ ] Reclamações (/reclamacoes)

### Integração
- [ ] Hooks de API
- [ ] React Query setup
- [ ] Error handling
- [ ] Loading states

---

**Nota:** Este documento substitui o repositório veris-frontend removido. Contém todas as informações essenciais para replicar o design e arquitetura.

---

**Última atualização:** 2025-11-17
**Status:** ✅ Referência completa
