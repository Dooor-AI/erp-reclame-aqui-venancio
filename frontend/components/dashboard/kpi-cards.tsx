'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { HelpCircle } from 'lucide-react';
import { useComplaintStats } from '@/hooks/use-analytics';

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

export function KPICards() {
  const { data: stats } = useComplaintStats();

  if (!stats) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Carregando...</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">-</div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Calculate resolution rate (accepts both 'Resolvido' and 'Resolvida')
  const resolved = (stats.by_status?.['Resolvido'] || 0) +
                   (stats.by_status?.['Resolvida'] || 0);
  const total = stats.total || 0;
  const resolutionRate = total > 0 ? ((resolved / total) * 100).toFixed(1) : '0.0';

  // Find top category
  const categoryEntries = Object.entries(stats.by_category || {});
  const topCategory = categoryEntries.length > 0
    ? categoryEntries.reduce((max, curr) => curr[1] > max[1] ? curr : max)
    : ['N/A', 0];

  // Count pending (not responded or not resolved - accepts variations)
  const pending = (stats.by_status?.['Não respondida'] || 0) +
                  (stats.by_status?.['Não resolvido'] || 0) +
                  (stats.by_status?.['Não resolvida'] || 0) +
                  (stats.by_status?.['Pendente'] || 0);

  return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
              Total de Reclamacoes
              <HelpTooltip content="Numero total de reclamacoes coletadas do Reclame Aqui para a empresa Drogaria Venancio." />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{total}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Coletadas do Reclame Aqui
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
              Taxa de Resolucao
              <HelpTooltip content="Porcentagem de reclamacoes marcadas como 'Resolvido' dividido pelo total. Formula: (Resolvidas / Total) x 100" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{resolutionRate}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              {resolved} de {total} resolvidas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
              Categoria Principal
              <HelpTooltip content="Categoria com maior numero de reclamacoes. As categorias sao extraidas do Reclame Aqui (ex: Entrega, Atendimento, Produto)." />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold truncate" title={topCategory[0] as string}>
              {topCategory[0]}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {topCategory[1]} reclamacoes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center">
              Pendentes
              <HelpTooltip content="Soma das reclamacoes com status 'Nao respondida' e 'Nao resolvido'. Indica casos que ainda precisam de atencao." />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">{pending}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Aguardando resposta/resolucao
            </p>
          </CardContent>
        </Card>
      </div>
  );
}
