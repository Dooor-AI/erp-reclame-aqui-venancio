'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useStoreTypeStats } from '@/hooks/use-analytics';

const COLORS = {
  physical: '#3b82f6',
  online: '#10b981',
  unknown: '#6b7280',
};

const LABELS = {
  physical: 'Loja Física',
  online: 'Online',
  unknown: 'Indefinido',
};

export function StoreTypeChart() {
  const [mounted, setMounted] = useState(false);
  const { data, isLoading, error } = useStoreTypeStats();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tipo de Loja</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Carregando...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data?.by_store_type) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tipo de Loja</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  const chartData = data.by_store_type.map((item: any) => ({
    name: LABELS[item.store_type as keyof typeof LABELS] || item.store_type,
    value: item.count,
    percentage: item.percentage,
    color: COLORS[item.store_type as keyof typeof COLORS] || '#6b7280',
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tipo de Loja (Física vs Online)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percentage }) => `${name}: ${percentage}%`}
              outerRadius={100}
              dataKey="value"
            >
              {chartData.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
