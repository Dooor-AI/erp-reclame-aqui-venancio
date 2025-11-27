'use client';

import { useState } from 'react';
import { useBenchmarkComparison, useBenchmarkBestResponses, useBenchmarkResponsePatterns, useBenchmarkStats } from '@/hooks/use-benchmark';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { CollapsibleSection } from '@/components/ui/collapsible-section';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export default function BenchmarkPage() {
  const { data: comparison, isLoading: loadingComparison } = useBenchmarkComparison();
  const { data: bestResponses, isLoading: loadingResponses } = useBenchmarkBestResponses({ limit: 10 });
  const { data: patterns, isLoading: loadingPatterns } = useBenchmarkResponsePatterns();
  const { data: stats, isLoading: loadingStats } = useBenchmarkStats();

  const [expandedResponse, setExpandedResponse] = useState<number | null>(null);

  if (loadingComparison || loadingStats) {
    return (
      <div className="space-y-8">
        <h2 className="text-3xl font-bold">Benchmark de Concorrentes</h2>
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </div>
    );
  }

  const getReputationColor = (reputation: string) => {
    switch (reputation) {
      case 'RA1000': return 'bg-purple-500';
      case 'Otimo':
      case 'Ótimo': return 'bg-green-500';
      case 'Bom': return 'bg-blue-500';
      case 'Regular': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 7) return 'text-blue-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Benchmark de Concorrentes</h2>
        <div className="text-sm text-muted-foreground">
          Análise comparativa com farmácias concorrentes
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Concorrentes Monitorados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.total_competitors || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Reclamações Coletadas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.total_complaints || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Com Respostas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.with_responses || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Nota 8+ (Boas Práticas)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">{stats?.high_score_responses || 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* Comparison Table */}
      <Card>
        <CardHeader>
          <CardTitle>Comparação com Concorrentes</CardTitle>
          <CardDescription>
            Métricas do Reclame Aqui comparadas com a Venâncio
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Empresa</TableHead>
                <TableHead>Reputação</TableHead>
                <TableHead className="text-right">Nota</TableHead>
                <TableHead className="text-right">Taxa Resposta</TableHead>
                <TableHead className="text-right">Taxa Solução</TableHead>
                <TableHead className="text-right">Voltaria a Comprar</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {comparison?.companies?.map((company: any) => (
                <TableRow
                  key={company.slug}
                  className={company.is_venancio ? 'bg-blue-50 font-semibold' : ''}
                >
                  <TableCell>
                    {company.name}
                    {company.is_venancio && (
                      <Badge variant="secondary" className="ml-2">Você</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge className={getReputationColor(company.reputation)}>
                      {company.reputation || 'N/A'}
                    </Badge>
                  </TableCell>
                  <TableCell className={`text-right ${getScoreColor(company.score || 0)}`}>
                    {company.score?.toFixed(1) || 'N/A'}
                  </TableCell>
                  <TableCell className="text-right">
                    {company.response_rate?.toFixed(1) || 'N/A'}%
                  </TableCell>
                  <TableCell className="text-right">
                    {company.solution_rate?.toFixed(1) || 'N/A'}%
                  </TableCell>
                  <TableCell className="text-right">
                    {company.would_buy_again?.toFixed(1) || 'N/A'}%
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Gap Analysis */}
          {comparison?.venancio_gaps && (
            <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <h4 className="font-semibold text-amber-800 mb-3">Gaps em relação à média dos concorrentes</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Nota</p>
                  <p className={`text-lg font-bold ${comparison.venancio_gaps.score > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {comparison.venancio_gaps.score > 0 ? '-' : '+'}{Math.abs(comparison.venancio_gaps.score).toFixed(1)} pts
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Taxa de Solução</p>
                  <p className={`text-lg font-bold ${comparison.venancio_gaps.solution_rate > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {comparison.venancio_gaps.solution_rate > 0 ? '-' : '+'}{Math.abs(comparison.venancio_gaps.solution_rate).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Voltaria a Comprar</p>
                  <p className={`text-lg font-bold ${comparison.venancio_gaps.would_buy_again > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {comparison.venancio_gaps.would_buy_again > 0 ? '-' : '+'}{Math.abs(comparison.venancio_gaps.would_buy_again).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Response Patterns */}
      <Card>
        <CardHeader>
          <CardTitle>Padrões de Respostas de Sucesso</CardTitle>
          <CardDescription>
            Análise do que funciona nas respostas bem avaliadas (nota 8+)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingPatterns ? (
            <Skeleton className="h-40" />
          ) : patterns?.total_analyzed === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Ainda não há dados suficientes. Execute o scraper de concorrentes primeiro.
            </p>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">{patterns?.patterns?.has_apology || 0}%</p>
                  <p className="text-sm text-muted-foreground">Incluem Desculpas</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">{patterns?.patterns?.has_solution || 0}%</p>
                  <p className="text-sm text-muted-foreground">Oferecem Solução</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-purple-600">{patterns?.patterns?.has_compensation || 0}%</p>
                  <p className="text-sm text-muted-foreground">Com Compensação</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-orange-600">{patterns?.patterns?.has_deadline || 0}%</p>
                  <p className="text-sm text-muted-foreground">Informam Prazo</p>
                </div>
              </div>

              {/* Recommendations */}
              {patterns?.recommendations && patterns.recommendations.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-semibold mb-3">Recomendações para Venâncio</h4>
                  <div className="space-y-2">
                    {patterns.recommendations.map((rec: any, idx: number) => (
                      <div key={idx} className={`p-3 rounded-lg border ${
                        rec.priority === 'high' ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'
                      }`}>
                        <div className="flex items-start gap-3">
                          <Badge variant={rec.priority === 'high' ? 'destructive' : 'secondary'}>
                            {rec.priority === 'high' ? 'Alta' : 'Média'}
                          </Badge>
                          <div>
                            <p className="font-medium">{rec.action}</p>
                            <p className="text-sm text-muted-foreground">{rec.reason}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Best Responses */}
      <CollapsibleSection title="Exemplos de Melhores Respostas" defaultOpen={false}>
        <div className="mt-4 space-y-4">
          {loadingResponses ? (
            <Skeleton className="h-40" />
          ) : !bestResponses || bestResponses.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Ainda não há respostas coletadas. Execute o scraper de concorrentes primeiro.
            </p>
          ) : (
            bestResponses.map((response: any) => (
              <Card key={response.id} className="overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base">{response.title}</CardTitle>
                      <CardDescription>{response.competitor_name}</CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      {response.was_resolved && (
                        <Badge variant="outline" className="bg-green-50 text-green-700">
                          Resolvido
                        </Badge>
                      )}
                      <Badge className="bg-green-600">
                        Nota {response.customer_score}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground uppercase mb-1">Reclamação</p>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {expandedResponse === response.id
                          ? response.complaint_text
                          : (response.complaint_text?.substring(0, 200) || 'N/A') + (response.complaint_text?.length > 200 ? '...' : '')}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground uppercase mb-1">Resposta da Empresa</p>
                      <p className="text-sm bg-blue-50 p-2 rounded border-l-4 border-blue-500">
                        {expandedResponse === response.id
                          ? response.company_response
                          : (response.company_response?.substring(0, 300) || 'N/A') + (response.company_response?.length > 300 ? '...' : '')}
                      </p>
                    </div>
                    {response.customer_evaluation && (
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase mb-1">Avaliação do Cliente</p>
                        <p className="text-sm bg-green-50 p-2 rounded">
                          {response.customer_evaluation?.substring(0, 200)}
                          {response.customer_evaluation?.length > 200 ? '...' : ''}
                        </p>
                      </div>
                    )}
                    <button
                      onClick={() => setExpandedResponse(expandedResponse === response.id ? null : response.id)}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      {expandedResponse === response.id ? 'Ver menos' : 'Ver mais'}
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </CollapsibleSection>

      {/* Instructions */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-lg">Como usar esta análise</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
            <li>Execute o scraper de concorrentes: <code className="bg-gray-200 px-1 rounded">python competitor_scraper.py</code></li>
            <li>Analise os padrões de resposta das empresas com melhor avaliação</li>
            <li>Use as recomendações para ajustar o gerador de respostas da Venâncio</li>
            <li>Monitore regularmente para acompanhar as mudanças no mercado</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
