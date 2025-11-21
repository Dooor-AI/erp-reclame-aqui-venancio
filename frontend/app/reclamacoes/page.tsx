'use client';

import { useState } from 'react';
import { useComplaints } from '@/hooks/use-complaints';
import { ReclamacaoCard } from '@/components/reclamacoes/reclamacao-card';
import { ResponseGeneratorDialog } from '@/components/respostas/response-generator-dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Complaint } from '@/lib/types';

export default function ReclamacoesPage() {
  const [sentimentFilter, setSentimentFilter] = useState<string | undefined>();
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: complaints, isLoading } = useComplaints({ sentiment: sentimentFilter });

  const handleGenerateResponse = (complaint: Complaint) => {
    setSelectedComplaint(complaint);
    setDialogOpen(true);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Reclamações</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Reclamações</h2>

        {/* Filtros */}
        <Select value={sentimentFilter} onValueChange={setSentimentFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filtrar por sentimento" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os sentimentos</SelectItem>
            <SelectItem value="Negativo">Negativo</SelectItem>
            <SelectItem value="Neutro">Neutro</SelectItem>
            <SelectItem value="Positivo">Positivo</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {complaints && complaints.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {complaints.map((complaint: Complaint) => (
            <ReclamacaoCard
              key={complaint.id}
              complaint={complaint}
              onGenerateResponse={() => handleGenerateResponse(complaint)}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-lg text-muted-foreground">Nenhuma reclamação encontrada</p>
        </div>
      )}

      {selectedComplaint && (
        <ResponseGeneratorDialog
          complaint={selectedComplaint}
          open={dialogOpen}
          onOpenChange={setDialogOpen}
        />
      )}
    </div>
  );
}
