'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Clock, CheckCircle, Calendar, HelpCircle, XCircle, Award, TrendingUp } from 'lucide-react';
import { useResponseMetrics } from '@/hooks/use-analytics';

function HelpTooltip({ content }: { content: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <HelpCircle className="h-3.5 w-3.5 text-muted-foreground cursor-help ml-1" />
      </TooltipTrigger>
      <TooltipContent className="max-w-[250px]">
        <p>{content}</p>
      </TooltipContent>
    </Tooltip>
  );
}

export function ResponseMetrics() {
  const { data, isLoading, error } = useResponseMetrics();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Metricas de Resposta</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Carregando...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Metricas de Resposta</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponivel</p>
        </CardContent>
      </Card>
    );
  }

  return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            Metricas de Resposta
            <HelpTooltip content="Metricas calculadas a partir das respostas da empresa as reclamacoes no Reclame Aqui." />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Response Rate */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{data.response_rate}%</div>
                <div className="text-xs text-muted-foreground flex items-center">
                  Taxa de Resposta
                  <HelpTooltip content="Porcentagem de reclamacoes que receberam resposta da empresa. Formula: (Com Resposta / Total) x 100" />
                </div>
              </div>
            </div>

            {/* Average Response Time */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Clock className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {data.avg_response_time_hours < 24
                    ? `${Math.round(data.avg_response_time_hours)}h`
                    : `${data.avg_response_time_days}d`}
                </div>
                <div className="text-xs text-muted-foreground flex items-center">
                  Tempo Medio
                  <HelpTooltip content="Media de tempo entre a data da reclamacao e a data da resposta da empresa. Calculado apenas para reclamacoes respondidas." />
                </div>
              </div>
            </div>

            {/* Resolution Rate */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 rounded-lg">
                <Award className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {data.resolution_rate ? `${data.resolution_rate}%` : 'N/A'}
                </div>
                <div className="text-xs text-muted-foreground flex items-center">
                  Taxa Resolucao
                  <HelpTooltip content="Porcentagem de reclamacoes marcadas como resolvidas. Formula: (Resolvidas / Total) x 100" />
                </div>
              </div>
            </div>

            {/* Without Response */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {data.total_complaints - data.with_response}
                </div>
                <div className="text-xs text-muted-foreground flex items-center">
                  Sem Resposta
                  <HelpTooltip content="Quantidade de reclamacoes que ainda nao receberam resposta da empresa." />
                </div>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="pt-4 border-t">
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">Total:</span>{' '}
                <span className="font-medium">{data.total_complaints}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Respondidas:</span>{' '}
                <span className="font-medium">{data.with_response}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Resolvidas:</span>{' '}
                <span className="font-medium">{data.resolved_count || 0}</span>
              </div>
            </div>
          </div>

          {/* Date Range */}
          {data.date_range && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>
                {data.date_range.oldest
                  ? `${data.date_range.oldest.slice(0, 10)} - ${data.date_range.newest?.slice(0, 10)}`
                  : 'Sem dados de data'}
              </span>
            </div>
          )}
        </CardContent>
      </Card>
  );
}
