'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { complaintsAPI } from '@/lib/api';

const STATUS_COLORS: Record<string, string> = {
  'Resolvida': '#22c55e',
  'Resolvido': '#22c55e',
  'Respondida': '#3b82f6',
  'ANSWERED': '#3b82f6',
  'Não respondida': '#ef4444',
  'Não resolvida': '#6b7280',
  'Não resolvido': '#f97316',
  'Em réplica': '#eab308',
};

export function StackedStatusByCategory() {
  const { data: complaints } = useQuery({
    queryKey: ['complaints-list-all'],
    queryFn: () => complaintsAPI.list({ limit: 1000 }),
  });

  if (!complaints || complaints.length === 0) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Status por Categoria (Empilhado)</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  // Build stacked data using tags (AI categories) instead of RA category
  const categoryData: Record<string, Record<string, number>> = {};
  const categoryCount: Record<string, number> = {};
  const statusSet = new Set<string>();

  complaints.forEach((complaint: any) => {
    const status = complaint.status || 'Sem status';
    statusSet.add(status);

    // Use tags (AI generated categories)
    const tags = complaint.tags || ['Sem categoria'];
    if (tags.length === 0) tags.push('Sem categoria');

    tags.forEach((tag: string) => {
      categoryCount[tag] = (categoryCount[tag] || 0) + 1;
      if (!categoryData[tag]) categoryData[tag] = {};
      categoryData[tag][status] = (categoryData[tag][status] || 0) + 1;
    });
  });

  // Get top 10 categories by count
  const topCategories = Object.entries(categoryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([cat]) => cat);

  const chartData = topCategories.map((category) => ({
    category: category.length > 20 ? category.substring(0, 20) + '...' : category,
    ...categoryData[category],
  }));

  const statuses = Array.from(statusSet);

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle>Status por Categoria (Empilhado)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" angle={-45} textAnchor="end" height={120} />
            <YAxis />
            <Tooltip />
            <Legend />
            {statuses.map((status) => (
              <Bar
                key={status}
                dataKey={status}
                stackId="a"
                fill={STATUS_COLORS[status] || '#94a3b8'}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
