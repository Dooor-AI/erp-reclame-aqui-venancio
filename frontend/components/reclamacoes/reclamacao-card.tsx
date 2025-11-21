import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Complaint } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface ReclamacaoCardProps {
  complaint: Complaint;
  onGenerateResponse: () => void;
}

export function ReclamacaoCard({ complaint, onGenerateResponse }: ReclamacaoCardProps) {
  const getSentimentColor = (sentiment?: string) => {
    if (sentiment === 'Negativo') return 'destructive';
    if (sentiment === 'Positivo') return 'default';
    return 'secondary';
  };

  const getUrgencyColor = (score?: number) => {
    if (!score) return 'secondary';
    if (score >= 7) return 'destructive';
    if (score >= 4) return 'outline';
    return 'default';
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg line-clamp-2">{complaint.title}</CardTitle>
          <div className="flex flex-col gap-2">
            {complaint.sentiment && (
              <Badge variant={getSentimentColor(complaint.sentiment)}>
                {complaint.sentiment}
              </Badge>
            )}
            {complaint.urgency_score != null && (
              <Badge variant={getUrgencyColor(complaint.urgency_score)}>
                Urgência: {complaint.urgency_score.toFixed(1)}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {complaint.text}
        </p>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-medium">{complaint.user_name}</span>
          <span>
            {formatDistanceToNow(new Date(complaint.scraped_at), {
              addSuffix: true,
              locale: ptBR,
            })}
          </span>
        </div>

        {!complaint.response_generated ? (
          <Button onClick={onGenerateResponse} className="w-full">
            Gerar Resposta
          </Button>
        ) : (
          <Badge variant="outline" className="w-full justify-center py-2">
            ✓ Resposta Gerada
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
