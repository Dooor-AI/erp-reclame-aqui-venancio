'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface StatusPieChartProps {
  data?: Record<string, number>;
}

const COLORS = ['#22c55e', '#3b82f6', '#eab308', '#ef4444', '#8b5cf6', '#06b6d4'];

// Mapeamento de status do Reclame Aqui para português (normalizado)
const STATUS_LABELS: Record<string, string> = {
  // Status em inglês da API
  'ANSWERED': 'Respondida',
  'PENDING': 'Pendente',
  'SOLVED': 'Resolvida',
  'NOT_SOLVED': 'Não Resolvida',
  'EVALUATED': 'Avaliada',
  // Status em português (variações)
  'Resolvido': 'Resolvida',
  'Resolvida': 'Resolvida',
  'Não Resolvido': 'Não Resolvida',
  'Não resolvida': 'Não Resolvida',
  'Respondida': 'Respondida',
  'Não respondida': 'Não Respondida',
  'Pendente': 'Pendente',
};

export function StatusPieChart({ data }: StatusPieChartProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Distribuição por Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-sm text-muted-foreground">Carregando...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Distribuição por Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  // Agregar dados com o mesmo nome normalizado
  const aggregatedData: Record<string, number> = {};
  Object.entries(data).forEach(([name, value]) => {
    const normalizedName = STATUS_LABELS[name] || name;
    aggregatedData[normalizedName] = (aggregatedData[normalizedName] || 0) + value;
  });

  const chartData = Object.entries(aggregatedData).map(([name, value]) => ({
    name,
    value,
  }));

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribuição por Status</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
        <div className="mt-4 text-center text-sm text-muted-foreground">
          Total: {total} reclamações
        </div>
      </CardContent>
    </Card>
  );
}
