'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';
import { complaintsAPI } from '@/lib/api';

interface HeatmapCell {
  category: string;
  status: string;
  count: number;
}

export function CategoryStatusHeatmap() {
  const { data: complaints } = useQuery({
    queryKey: ['complaints-list-all'],
    queryFn: () => complaintsAPI.list({ limit: 1000 }),
  });

  if (!complaints || complaints.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Matriz: Categoria x Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  // Build matrix data using tags (AI categories) instead of RA category
  const matrix: Record<string, Record<string, number>> = {};
  const categoryCount: Record<string, number> = {};
  const statuses = new Set<string>();

  complaints.forEach((complaint: any) => {
    const status = complaint.status || 'Sem status';
    statuses.add(status);

    // Use tags (AI generated categories) - each complaint can have multiple tags
    const tags = complaint.tags || ['Sem categoria'];
    if (tags.length === 0) tags.push('Sem categoria');

    tags.forEach((tag: string) => {
      categoryCount[tag] = (categoryCount[tag] || 0) + 1;
      if (!matrix[tag]) matrix[tag] = {};
      matrix[tag][status] = (matrix[tag][status] || 0) + 1;
    });
  });

  // Get top 10 categories by count
  const topCategories = Object.entries(categoryCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([cat]) => cat);

  const categoryArray = topCategories;
  const statusArray = Array.from(statuses).sort();

  // Find max count for color scaling
  const maxCount = Math.max(
    ...Object.values(matrix).flatMap(statusCounts => Object.values(statusCounts))
  );

  const getBackgroundColor = (count: number) => {
    if (!count) return 'bg-gray-100';
    const intensity = Math.min(Math.floor((count / maxCount) * 5), 5);
    const colors = ['bg-blue-100', 'bg-blue-200', 'bg-blue-300', 'bg-blue-400', 'bg-blue-500'];
    return colors[intensity - 1] || 'bg-gray-100';
  };

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle>Matriz: Categoria x Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr>
                <th className="border p-2 bg-gray-50 text-left font-semibold">Categoria</th>
                {statusArray.map(status => (
                  <th key={status} className="border p-2 bg-gray-50 text-center font-semibold">
                    {status}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {categoryArray.map(category => (
                <tr key={category}>
                  <td className="border p-2 font-medium">{category}</td>
                  {statusArray.map(status => {
                    const count = matrix[category]?.[status] || 0;
                    return (
                      <td
                        key={`${category}-${status}`}
                        className={`border p-2 text-center ${getBackgroundColor(count)}`}
                      >
                        {count || '-'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex items-center gap-4 text-xs text-muted-foreground">
          <span>Intensidade:</span>
          <div className="flex gap-1">
            <div className="w-6 h-4 bg-gray-100 border" title="0" />
            <div className="w-6 h-4 bg-blue-100 border" title="Baixa" />
            <div className="w-6 h-4 bg-blue-200 border" />
            <div className="w-6 h-4 bg-blue-300 border" />
            <div className="w-6 h-4 bg-blue-400 border" />
            <div className="w-6 h-4 bg-blue-500 border" title="Alta" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
