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
      </div>
    </div>
  );
}
