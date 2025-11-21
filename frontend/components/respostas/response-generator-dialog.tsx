'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useGenerateResponse } from '@/hooks/use-complaints';
import { Complaint } from '@/lib/types';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Skeleton } from '@/components/ui/skeleton';

interface ResponseGeneratorDialogProps {
  complaint: Complaint;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ResponseGeneratorDialog({ complaint, open, onOpenChange }: ResponseGeneratorDialogProps) {
  const [editedResponse, setEditedResponse] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const { mutate: generate, data, isPending, reset } = useGenerateResponse(complaint.id);

  // Update editedResponse when data changes
  useEffect(() => {
    if (data?.response) {
      setEditedResponse(data.response);
    }
  }, [data]);

  // Reset when dialog opens/closes or complaint changes
  useEffect(() => {
    if (!open) {
      reset(); // Clear previous response data
      setEditedResponse('');
      setIsAnalyzing(false);
    }
  }, [open, complaint.id, reset]);

  const handleGenerate = async () => {
    try {
      // First, check if complaint needs analysis
      if (!complaint.sentiment || complaint.sentiment === 'Unknown') {
        setIsAnalyzing(true);
        toast.info('Analisando reclamação...');

        const analyzeResponse = await fetch(`http://localhost:3003/analytics/analyze/${complaint.id}`, {
          method: 'POST',
        });

        if (!analyzeResponse.ok) {
          throw new Error('Falha na análise da reclamação');
        }

        setIsAnalyzing(false);
        toast.success('Análise concluída!');

        // Wait a bit for the analysis to be saved
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Now generate the response
      generate(undefined, {
        onSuccess: (data: any) => {
          setEditedResponse(data.response || data.edited_response || '');
          toast.success('Resposta gerada com sucesso!');
        },
        onError: (error) => {
          toast.error('Erro ao gerar resposta: ' + error.message);
        },
      });
    } catch (error: any) {
      setIsAnalyzing(false);
      toast.error('Erro: ' + error.message);
    }
  };

  const handleSend = () => {
    // Mock: apenas mostrar toast
    toast.success('Resposta enviada! (simulação)');
    onOpenChange(false);
  };

  const handleClose = () => {
    reset(); // Clear mutation data
    setEditedResponse('');
    setIsAnalyzing(false);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Gerar Resposta - {complaint.title}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Complaint Info */}
          <div className="bg-muted p-4 rounded-md">
            <p className="text-sm font-medium mb-2">Reclamação:</p>
            <p className="text-sm text-muted-foreground">{complaint.text}</p>
          </div>

          {!data ? (
            <Button onClick={handleGenerate} disabled={isPending || isAnalyzing} className="w-full">
              {isAnalyzing ? 'Analisando reclamação...' : isPending ? 'Gerando resposta...' : 'Gerar Resposta com IA'}
            </Button>
          ) : (
            <>
              {isPending ? (
                <div className="space-y-2">
                  <Skeleton className="h-32" />
                  <Skeleton className="h-20" />
                </div>
              ) : (
                <>
                  <div>
                    <label className="text-sm font-medium">Resposta Gerada:</label>
                    <Textarea
                      value={editedResponse}
                      onChange={(e) => setEditedResponse(e.target.value)}
                      rows={8}
                      className="mt-2"
                      placeholder="A resposta gerada aparecerá aqui..."
                    />
                  </div>

                  {data.coupon && (
                    <div className="bg-muted p-4 rounded-md">
                      <p className="text-sm font-medium">Cupom de Desconto:</p>
                      <p className="text-2xl font-bold mt-2">{data.coupon.code}</p>
                      <p className="text-sm text-muted-foreground">
                        {data.coupon.discount}% de desconto
                      </p>
                      {data.coupon.valid_until && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Válido até: {new Date(data.coupon.valid_until).toLocaleDateString('pt-BR')}
                        </p>
                      )}
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button variant="outline" className="flex-1" onClick={handleClose}>
                      Cancelar
                    </Button>
                    <Button onClick={handleSend} className="flex-1" disabled={!editedResponse}>
                      Enviar (Mock)
                    </Button>
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
