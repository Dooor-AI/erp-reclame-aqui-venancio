# 📋 Order for Chat D - Round 1

**From:** Commander
**To:** Chat D
**Date:** 2025-11-17
**Priority:** 🟠 High
**Estimated Duration:** 10-12 hours (Dias 2-5, paralelo)

---

## 🎯 Mission

Criar interface web moderna com Next.js 15 para visualização de reclamações, estatísticas e geração de respostas, seguindo o padrão do veris-frontend.

---

## 📋 Background

Precisamos de um dashboard profissional para demonstrar o sistema RPA. Deve seguir a arquitetura do veris-frontend: Next.js 15, TypeScript, Tailwind CSS v4, Shadcn/ui, Zustand, React Query.

**Dependencies:**
- ⚠️ **Chat A** em 30% (API básica funcionando)
- ⚠️ **Chat B** em 50% (para estatísticas)
- ⚠️ **Chat C** completo (para gerador de respostas)

**Você pode começar em paralelo desde o Dia 2!**

---

## 🚀 Your Tasks

### Task 1: Setup do Projeto Frontend (2h)
**Início:** Dia 2 (quando Chat A tiver API básica)

**Steps:**

1. Criar projeto Next.js 15:
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
```

2. Instalar dependências:
```bash
npm install @tanstack/react-query zustand
npm install @shadcn/ui
npx shadcn-ui@latest init
npm install recharts framer-motion lucide-react
npm install clsx tailwind-merge class-variance-authority
npm install sonner # Toast notifications
npm install date-fns # Date formatting
```

3. Configurar Shadcn/ui:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add table
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add select
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add tabs
```

4. Criar estrutura de pastas:
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx (dashboard)
│   ├── reclamacoes/
│   │   └── page.tsx
│   └── globals.css
├── components/
│   ├── ui/ (Shadcn/ui)
│   ├── layout/
│   │   ├── header.tsx
│   │   └── sidebar.tsx
│   ├── dashboard/
│   │   ├── stats-card.tsx
│   │   ├── sentiment-chart.tsx
│   │   └── category-chart.tsx
│   ├── reclamacoes/
│   │   ├── reclamacao-card.tsx
│   │   ├── reclamacao-table.tsx
│   │   └── filters.tsx
│   └── respostas/
│       ├── response-generator-dialog.tsx
│       └── response-editor.tsx
├── lib/
│   ├── api.ts
│   ├── utils.ts
│   └── types.ts
├── hooks/
│   ├── use-complaints.ts
│   └── use-analytics.ts
├── store/
│   └── appStore.ts
└── package.json
```

5. Configurar API client em `lib/api.ts`:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

// Complaints API
export const complaintsAPI = {
  list: (params?: { skip?: number; limit?: number; sentiment?: string }) =>
    apiRequest(`/complaints?${new URLSearchParams(params as any)}`),

  get: (id: number) => apiRequest(`/complaints/${id}`),

  stats: () => apiRequest(`/complaints/stats`),
};

// Analytics API
export const analyticsAPI = {
  analyze: (id: number) => apiRequest(`/analytics/analyze/${id}`, { method: 'POST' }),

  sentimentStats: () => apiRequest(`/analytics/stats/sentiment`),

  categoryStats: () => apiRequest(`/analytics/stats/categories`),

  urgencyStats: () => apiRequest(`/analytics/stats/urgency`),
};

// Responses API
export const responsesAPI = {
  generate: (id: number) => apiRequest(`/responses/generate/${id}`, { method: 'POST' }),

  get: (id: number) => apiRequest(`/responses/${id}`),

  edit: (id: number, text: string) =>
    apiRequest(`/responses/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ edited_response: text }),
    }),

  markSent: (id: number) => apiRequest(`/responses/${id}/send`, { method: 'POST' }),
};
```

6. Criar types em `lib/types.ts`:
```typescript
export interface Complaint {
  id: number;
  title: string;
  text: string;
  user_name: string;
  complaint_date: string;
  status: string;
  sentiment?: string;
  sentiment_score?: number;
  urgency_score?: number;
  response_generated?: string;
  coupon_code?: string;
  scraped_at: string;
}

export interface ComplaintStats {
  total: number;
  by_sentiment: Record<string, number>;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  avg_urgency: number;
}
```

**Expected Result:**
- ✅ Projeto Next.js configurado
- ✅ Dependências instaladas
- ✅ Estrutura de pastas criada
- ✅ API client configurado
- ✅ Rodando em `http://localhost:3000`

---

### Task 2: Componentes Base + Layout (2h)

Criar `components/layout/header.tsx`:
```typescript
export function Header() {
  return (
    <header className="border-b bg-white">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Venâncio RPA</h1>
        <nav className="flex gap-4">
          <a href="/" className="text-sm hover:underline">Dashboard</a>
          <a href="/reclamacoes" className="text-sm hover:underline">Reclamações</a>
        </nav>
      </div>
    </header>
  );
}
```

Criar `app/layout.tsx`:
```typescript
import { QueryProvider } from '@/components/query-provider';
import { Header } from '@/components/layout/header';
import { Toaster } from '@/components/ui/toaster';
import './globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <QueryProvider>
          <Header />
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}
```

Criar `components/query-provider.tsx`:
```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 min
        retry: 1,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

---

### Task 3: Dashboard com Estatísticas (3h)

Criar hook `hooks/use-analytics.ts`:
```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { complaintsAPI, analyticsAPI } from '@/lib/api';

export function useComplaintStats() {
  return useQuery({
    queryKey: ['complaint-stats'],
    queryFn: () => complaintsAPI.stats(),
  });
}

export function useSentimentStats() {
  return useQuery({
    queryKey: ['sentiment-stats'],
    queryFn: () => analyticsAPI.sentimentStats(),
  });
}
```

Criar `components/dashboard/stats-card.tsx`:
```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
}

export function StatsCard({ title, value, description, icon }: StatsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && <p className="text-xs text-muted-foreground">{description}</p>}
      </CardContent>
    </Card>
  );
}
```

Criar `components/dashboard/sentiment-chart.tsx` (Pie chart com Recharts)

Criar `app/page.tsx`:
```typescript
'use client';

import { useComplaintStats } from '@/hooks/use-analytics';
import { StatsCard } from '@/components/dashboard/stats-card';
import { SentimentChart } from '@/components/dashboard/sentiment-chart';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardPage() {
  const { data: stats, isLoading } = useComplaintStats();

  if (isLoading) return <div>Carregando...</div>;

  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold">Dashboard</h2>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total de Reclamações"
          value={stats?.total || 0}
        />
        <StatsCard
          title="Negativas"
          value={stats?.by_sentiment?.Negativo || 0}
        />
        <StatsCard
          title="Urgência Média"
          value={stats?.avg_urgency?.toFixed(1) || '0'}
        />
        <StatsCard
          title="Taxa de Resposta"
          value="85%"
        />
      </div>

      {/* Gráficos */}
      <div className="grid gap-4 md:grid-cols-2">
        <SentimentChart data={stats?.by_sentiment} />
        {/* Adicionar CategoryChart */}
      </div>
    </div>
  );
}
```

**Expected Result:**
- ✅ Dashboard com KPIs
- ✅ Gráficos de sentimento e categorias
- ✅ Loading states
- ✅ Design responsivo

---

### Task 4: Página de Reclamações (3h)

Criar `hooks/use-complaints.ts`:
```typescript
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { complaintsAPI, responsesAPI } from '@/lib/api';

export function useComplaints(filters?: { sentiment?: string }) {
  return useQuery({
    queryKey: ['complaints', filters],
    queryFn: () => complaintsAPI.list(filters),
  });
}

export function useGenerateResponse(complaintId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => responsesAPI.generate(complaintId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['complaints'] });
    },
  });
}
```

Criar `components/reclamacoes/reclamacao-card.tsx`:
```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Complaint } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface ReclamacaoCardProps {
  complaint: Complaint;
  onGenerateResponse: () => void;
}

export function ReclamacaoCard({ complaint, onGenerateResponse }: ReclamacaoCardProps) {
  const getSentimentColor = (sentiment?: string) => {
    if (sentiment === 'Negativo') return 'destructive';
    if (sentiment === 'Positivo') return 'default';
    return 'secondary';
  };

  const getUrgencyColor = (score?: number) => {
    if (!score) return 'secondary';
    if (score >= 7) return 'destructive';
    if (score >= 4) return 'warning';
    return 'default';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg">{complaint.title}</CardTitle>
          <div className="flex gap-2">
            {complaint.sentiment && (
              <Badge variant={getSentimentColor(complaint.sentiment)}>
                {complaint.sentiment}
              </Badge>
            )}
            {complaint.urgency_score && (
              <Badge variant={getUrgencyColor(complaint.urgency_score)}>
                Urgência: {complaint.urgency_score.toFixed(1)}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {complaint.text}
        </p>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{complaint.user_name}</span>
          <span>
            {formatDistanceToNow(new Date(complaint.scraped_at), {
              addSuffix: true,
              locale: ptBR,
            })}
          </span>
        </div>

        {!complaint.response_generated ? (
          <Button onClick={onGenerateResponse} className="w-full">
            Gerar Resposta
          </Button>
        ) : (
          <Badge variant="outline" className="w-full justify-center">
            ✓ Resposta Gerada
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
```

Criar `app/reclamacoes/page.tsx`:
```typescript
'use client';

import { useComplaints, useGenerateResponse } from '@/hooks/use-complaints';
import { ReclamacaoCard } from '@/components/reclamacoes/reclamacao-card';
import { Select } from '@/components/ui/select';
import { useState } from 'react';

export default function ReclamacoesPage() {
  const [sentimentFilter, setSentimentFilter] = useState<string>();
  const { data: complaints, isLoading } = useComplaints({ sentiment: sentimentFilter });

  const handleGenerate = (id: number) => {
    // Implementar dialog com gerador
  };

  if (isLoading) return <div>Carregando...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Reclamações</h2>

        {/* Filtros */}
        <Select onValueChange={setSentimentFilter}>
          <option value="">Todos os sentimentos</option>
          <option value="Negativo">Negativo</option>
          <option value="Neutro">Neutro</option>
          <option value="Positivo">Positivo</option>
        </Select>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {complaints?.map((complaint) => (
          <ReclamacaoCard
            key={complaint.id}
            complaint={complaint}
            onGenerateResponse={() => handleGenerate(complaint.id)}
          />
        ))}
      </div>
    </div>
  );
}
```

---

### Task 5: Gerador de Respostas (Dialog) (2h)

Criar `components/respostas/response-generator-dialog.tsx`:
```typescript
'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useGenerateResponse } from '@/hooks/use-complaints';
import { useState } from 'react';
import { toast } from 'sonner';

export function ResponseGeneratorDialog({ complaintId, open, onOpenChange }) {
  const [editedResponse, setEditedResponse] = useState('');
  const { mutate: generate, data, isLoading } = useGenerateResponse(complaintId);

  const handleGenerate = () => {
    generate(undefined, {
      onSuccess: (data) => {
        setEditedResponse(data.response);
        toast.success('Resposta gerada com sucesso!');
      },
      onError: () => {
        toast.error('Erro ao gerar resposta');
      },
    });
  };

  const handleSend = () => {
    // Mock: apenas mostrar toast
    toast.success('Resposta enviada! (simulação)');
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Gerar Resposta</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {!data ? (
            <Button onClick={handleGenerate} disabled={isLoading} className="w-full">
              {isLoading ? 'Gerando...' : 'Gerar Resposta com IA'}
            </Button>
          ) : (
            <>
              <div>
                <label className="text-sm font-medium">Resposta Gerada:</label>
                <Textarea
                  value={editedResponse}
                  onChange={(e) => setEditedResponse(e.target.value)}
                  rows={8}
                  className="mt-2"
                />
              </div>

              <div className="bg-muted p-4 rounded-md">
                <p className="text-sm font-medium">Cupom de Desconto:</p>
                <p className="text-2xl font-bold mt-2">{data.coupon?.code}</p>
                <p className="text-sm text-muted-foreground">
                  {data.coupon?.discount}% de desconto
                </p>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" className="flex-1">
                  Editar
                </Button>
                <Button onClick={handleSend} className="flex-1">
                  Enviar (Mock)
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

Integrar no `ReclamacaoCard`

---

## 📝 Deliverables

1. **`answer_chat_D_1.md`** - Results with screenshots
2. **Frontend code** - All components
3. **README.md** - Setup instructions
4. **Screenshots** - Dashboard e reclamações

---

## ⏰ Time Tracking

```markdown
| Task | Estimated | Actual | Status |
|------|-----------|--------|--------|
| Task 1: Setup | 2h | - | ⏳ |
| Task 2: Layout | 2h | - | ⏳ |
| Task 3: Dashboard | 3h | - | ⏳ |
| Task 4: Reclamações | 3h | - | ⏳ |
| Task 5: Generator | 2h | - | ⏳ |
```

---

## 🎯 Success Criteria

- ✅ Frontend rodando em localhost:3000
- ✅ Dashboard com estatísticas em tempo real
- ✅ Listagem de reclamações com filtros
- ✅ Gerador de respostas integrado
- ✅ Design profissional e responsivo
- ✅ Loading states e error handling

---

## 📞 Questions?

**Bloqueadores:**
- API não disponível → Mock dados temporariamente
- Chat C não completo → Desabilitar gerador temporariamente

---

## 🔄 Related Tasks

- **Chat A, B, C** fornecem as APIs
- **Chat E** documentará o frontend

**You can start early and work in parallel!**

---

**Start on Day 2! Good luck! 🚀**
