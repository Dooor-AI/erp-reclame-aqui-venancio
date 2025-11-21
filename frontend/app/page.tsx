'use client';

import { useComplaintStats, useTimelineStats, useLocationStats } from '@/hooks/use-analytics';
import { KPICards } from '@/components/dashboard/kpi-cards';
import { StatusPieChart } from '@/components/dashboard/status-pie-chart';
import { CategoryChart } from '@/components/dashboard/category-chart';
import { TimelineChart } from '@/components/dashboard/timeline-chart';
import { LocationChart } from '@/components/dashboard/location-chart';
import { CategoryStatusHeatmap } from '@/components/dashboard/category-status-heatmap';
import { StackedStatusByCategory } from '@/components/dashboard/stacked-status-by-category';
import { ComplaintsTable } from '@/components/dashboard/complaints-table';
import { CollapsibleSection } from '@/components/ui/collapsible-section';
import { Skeleton } from '@/components/ui/skeleton';
import { StoreTypeChart } from '@/components/dashboard/store-type-chart';
import { TagsCloud } from '@/components/dashboard/tags-cloud';
import { WeeklyTrends } from '@/components/dashboard/weekly-trends';
import { ResponseMetrics } from '@/components/dashboard/response-metrics';

export default function DashboardPage() {
  const { data: stats, isLoading } = useComplaintStats();
  const { data: timelineData } = useTimelineStats(30);
  const { data: locationData } = useLocationStats(20);

  if (isLoading) {
    return (
      <div className="space-y-8">
        <h2 className="text-3xl font-bold">Dashboard</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  // Calculate resolution rate for system info
  const resolved = stats?.by_status?.['Resolvido'] || 0;
  const total = stats?.total || 0;
  const resolutionRate = total > 0 ? ((resolved / total) * 100).toFixed(1) : '0.0';

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Dashboard</h2>
        <div className="text-sm text-muted-foreground">
          Última atualização: {new Date().toLocaleTimeString('pt-BR')}
        </div>
      </div>

      {/* KPIs - Always visible at the top */}
      <KPICards />

      {/* New Features: Weekly Trends and Response Metrics */}
      <div className="grid gap-4 md:grid-cols-2">
        <WeeklyTrends />
        <ResponseMetrics />
      </div>

      {/* Main Charts - Always visible */}
      <div className="grid gap-4 md:grid-cols-2">
        <StatusPieChart data={stats?.by_status} />
        <CategoryChart data={stats?.by_category} />
      </div>

      {/* Store Type and Tags */}
      <div className="grid gap-4 md:grid-cols-2">
        <StoreTypeChart />
        <TagsCloud />
      </div>

      {/* Timeline - Always visible */}
      <TimelineChart data={timelineData?.timeline} />

      {/* Collapsible Sections for Additional Charts */}
      <div className="space-y-4">
        <CollapsibleSection title="Análises Avançadas" defaultOpen={false}>
          <div className="space-y-4 mt-4">
            <CategoryStatusHeatmap />
            <StackedStatusByCategory />
          </div>
        </CollapsibleSection>

        <CollapsibleSection title="Análise Geográfica" defaultOpen={false}>
          <div className="mt-4">
            <LocationChart data={locationData?.locations} />
          </div>
        </CollapsibleSection>

        <CollapsibleSection title="Tabela Completa de Reclamações" defaultOpen={false}>
          <div className="mt-4">
            <ComplaintsTable />
          </div>
        </CollapsibleSection>

        <CollapsibleSection title="Informações do Sistema" defaultOpen={false}>
          <div className="mt-4">
            <SystemInfo stats={stats} resolutionRate={resolutionRate} />
          </div>
        </CollapsibleSection>
      </div>
    </div>
  );
}

function SystemInfo({ stats, resolutionRate }: { stats: any; resolutionRate: string }) {
  if (!stats) {
    return <p className="text-muted-foreground">Carregando...</p>;
  }

  const total = stats.total || 0;
  const categoryEntries = Object.entries(stats.by_category || {});
  const statusEntries = Object.entries(stats.by_status || {});

  const withCategory = categoryEntries.reduce((sum, [_, count]) => sum + (count as number), 0);
  const categoryRate = total > 0 ? ((withCategory / total) * 100).toFixed(1) : '0.0';

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-bold mb-4">Status do Scraper</h4>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Total de Reclamações:</span>
            <span className="font-semibold">{total}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Categorias Únicas:</span>
            <span className="font-semibold">{categoryEntries.length}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Status Únicos:</span>
            <span className="font-semibold">{statusEntries.length}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Fonte:</span>
            <span className="text-xs font-mono">Reclame Aqui</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-bold mb-4">Qualidade dos Dados</h4>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm text-muted-foreground">Taxa de Categorização:</span>
              <span className="font-semibold">{categoryRate}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full"
                style={{ width: `${categoryRate}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm text-muted-foreground">Taxa de Resolução:</span>
              <span className="font-semibold">{resolutionRate}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${resolutionRate}%` }}
              />
            </div>
          </div>

          <div className="pt-2 text-xs text-muted-foreground">
            <p>Última coleta: {new Date().toLocaleString('pt-BR')}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border p-6 md:col-span-2">
        <h4 className="text-lg font-bold mb-4">Top 5 Categorias</h4>
        <div className="space-y-3">
          {categoryEntries
            .sort(([_, a], [__, b]) => (b as number) - (a as number))
            .slice(0, 5)
            .map(([category, count]) => (
              <div key={category}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium truncate" title={category}>
                    {category}
                  </span>
                  <span className="text-sm font-semibold">{count as number}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${total > 0 ? ((count as number) / total) * 100 : 0}%` }}
                  />
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
