'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useWeeklyTrends } from '@/hooks/use-analytics';

export function WeeklyTrends() {
  const { data, isLoading, error } = useWeeklyTrends();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tendências da Semana</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Carregando...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data?.summary) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tendências da Semana</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  const { summary, daily_breakdown, sentiment_this_week, store_type_this_week, top_tags_this_week } = data;

  const TrendIcon = summary.trend_direction === 'up'
    ? TrendingUp
    : summary.trend_direction === 'down'
    ? TrendingDown
    : Minus;

  const trendColor = summary.trend_direction === 'up'
    ? 'text-red-500'
    : summary.trend_direction === 'down'
    ? 'text-green-500'
    : 'text-gray-500';

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Tendências da Semana
          <TrendIcon className={`h-5 w-5 ${trendColor}`} />
        </CardTitle>
        <CardDescription>
          {data.period?.start} a {data.period?.end}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{summary.this_week}</div>
            <div className="text-xs text-muted-foreground">Esta Semana</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{summary.last_week}</div>
            <div className="text-xs text-muted-foreground">Semana Anterior</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${trendColor}`}>
              {summary.trend_percentage > 0 ? '+' : ''}{summary.trend_percentage}%
            </div>
            <div className="text-xs text-muted-foreground">Variação</div>
          </div>
        </div>

        {/* Daily Chart */}
        {daily_breakdown && daily_breakdown.length > 0 && (
          <ResponsiveContainer width="100%" height={150}>
            <AreaChart data={daily_breakdown}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => value.slice(5)} // Show only MM-DD
              />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {/* Sentiment breakdown */}
        <div>
          <div className="text-sm font-medium mb-2">Sentimento</div>
          <div className="flex gap-2">
            <Badge variant="destructive">Negativo: {sentiment_this_week?.Negativo || 0}</Badge>
            <Badge variant="secondary">Neutro: {sentiment_this_week?.Neutro || 0}</Badge>
            <Badge variant="default">Positivo: {sentiment_this_week?.Positivo || 0}</Badge>
          </div>
        </div>

        {/* Store type breakdown */}
        <div>
          <div className="text-sm font-medium mb-2">Tipo de Loja</div>
          <div className="flex gap-2">
            <Badge variant="outline">Física: {store_type_this_week?.physical || 0}</Badge>
            <Badge variant="outline">Online: {store_type_this_week?.online || 0}</Badge>
          </div>
        </div>

        {/* Top tags */}
        {top_tags_this_week && top_tags_this_week.length > 0 && (
          <div>
            <div className="text-sm font-medium mb-2">Top Tags</div>
            <div className="flex flex-wrap gap-1">
              {top_tags_this_week.slice(0, 5).map((item: any) => (
                <Badge key={item.tag} variant="outline" className="text-xs">
                  {item.tag} ({item.count})
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
