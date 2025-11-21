'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useTagStats } from '@/hooks/use-analytics';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e', '#f97316'];

export function TagsCloud() {
  const { data, isLoading, error } = useTagStats(30);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Distribuicao de Tags</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Carregando...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data?.all_tags) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Distribuicao de Tags</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponivel</p>
        </CardContent>
      </Card>
    );
  }

  // Use all_tags for the distribution chart (already sorted by frequency)
  const chartData = data.all_tags.slice(0, 10).map((item: any) => ({
    name: item.tag.length > 15 ? item.tag.substring(0, 15) + '...' : item.tag,
    fullName: item.tag,
    count: item.count
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribuicao de Tags</CardTitle>
        <CardDescription>
          Tags mais frequentes nas reclamacoes analisadas
        </CardDescription>
      </CardHeader>
      <CardContent>
        {chartData.length > 0 ? (
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <XAxis type="number" />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={100}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  formatter={(value: number, name: string, props: any) => [
                    value,
                    props.payload.fullName
                  ]}
                  labelFormatter={() => ''}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Nenhuma tag disponivel</p>
        )}
        <div className="mt-4 text-xs text-muted-foreground">
          Total de tags unicas: {data.total_unique_tags}
        </div>
      </CardContent>
    </Card>
  );
}
