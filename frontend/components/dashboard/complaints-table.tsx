'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useQuery } from '@tanstack/react-query';
import { complaintsAPI } from '@/lib/api';

// Helper to get category from classification array or tags
const getCategory = (complaint: any): string => {
  // First try classification array
  if (complaint.classification && Array.isArray(complaint.classification) && complaint.classification.length > 0) {
    return complaint.classification[0];
  }
  // Fallback to tags
  if (complaint.tags && Array.isArray(complaint.tags) && complaint.tags.length > 0) {
    // Map common tags to categories
    const tagToCat: Record<string, string> = {
      'atraso-entrega': 'Entrega',
      'produto-indisponivel': 'Estoque',
      'atendimento-ruim': 'Atendimento',
      'erro-sistema': 'Sistema',
      'estorno-pendente': 'Financeiro',
      'troca-recusada': 'Troca/Devolucao',
      'cancelamento-problematico': 'Cancelamento',
      'cobranca-indevida': 'Financeiro',
      'produto-danificado': 'Produto',
      'preco-errado': 'Preco',
    };
    for (const tag of complaint.tags) {
      if (tagToCat[tag]) return tagToCat[tag];
    }
    // Return first tag formatted
    return complaint.tags[0].replace(/-/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
  }
  return '';
};

export function ComplaintsTable() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const { data: complaints, isLoading } = useQuery({
    queryKey: ['complaints-list-all'],
    queryFn: () => complaintsAPI.list({ limit: 1000 }),
  });

  if (isLoading) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Lista de Reclamacoes</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Carregando...</p>
        </CardContent>
      </Card>
    );
  }

  if (!complaints || complaints.length === 0) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Lista de Reclamacoes</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponivel</p>
        </CardContent>
      </Card>
    );
  }

  // Extract unique statuses and categories from complaints
  const statuses = Array.from(new Set(complaints.map((c: any) => c.status).filter(Boolean)));
  const categories = Array.from(new Set(complaints.map((c: any) => getCategory(c)).filter(Boolean)));

  // Filter complaints
  const filteredComplaints = complaints.filter((complaint: any) => {
    const matchesSearch = searchTerm === '' ||
      complaint.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      complaint.text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      complaint.user_name?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'all' || complaint.status === statusFilter;
    const category = getCategory(complaint);
    const matchesCategory = categoryFilter === 'all' || category === categoryFilter;

    return matchesSearch && matchesStatus && matchesCategory;
  });

  // Status badge colors based on Reclame Aqui statuses
  const getStatusBadgeColor = (status: string) => {
    if (!status) return 'bg-gray-100 text-gray-800';

    // Normalize: remove accents and convert to lowercase
    const s = status
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, ''); // Remove diacritics

    // Not responded - RED (check first, most specific)
    if (s.includes('nao respondida') || s.includes('não respondida') || s === 'pendente') {
      return 'bg-red-500 text-white';
    }
    // Not resolved - YELLOW/AMBER
    if (s.includes('nao resolvida') || s.includes('não resolvida')) {
      return 'bg-amber-500 text-white';
    }
    // Resolved - GREEN
    if (s.includes('resolvid') || s.includes('finalizado')) {
      return 'bg-green-500 text-white';
    }
    // Responded/Answered - BLUE
    if (s.includes('respondida') || s.includes('respondido')) {
      return 'bg-blue-500 text-white';
    }
    // Awaiting reply/replica - ORANGE
    if (s.includes('replica') || s.includes('aguardando')) {
      return 'bg-orange-500 text-white';
    }
    // In progress/analysis - PURPLE
    if (s.includes('andamento') || s.includes('analise')) {
      return 'bg-purple-500 text-white';
    }
    // Evaluated - TEAL
    if (s.includes('avaliada') || s.includes('avaliado')) {
      return 'bg-teal-500 text-white';
    }

    return 'bg-gray-500 text-white';
  };

  // Category badge colors
  const getCategoryBadgeColor = (category: string) => {
    if (!category) return 'bg-gray-100 text-gray-700 border-gray-300';
    const c = category.toLowerCase();

    if (c.includes('entrega')) return 'bg-orange-100 text-orange-800 border-orange-300';
    if (c.includes('atendimento')) return 'bg-pink-100 text-pink-800 border-pink-300';
    if (c.includes('financeiro') || c.includes('cobranca') || c.includes('estorno')) return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    if (c.includes('produto') || c.includes('estoque')) return 'bg-blue-100 text-blue-800 border-blue-300';
    if (c.includes('sistema') || c.includes('site') || c.includes('app')) return 'bg-violet-100 text-violet-800 border-violet-300';
    if (c.includes('troca') || c.includes('devolucao')) return 'bg-amber-100 text-amber-800 border-amber-300';
    if (c.includes('cancelamento')) return 'bg-red-100 text-red-800 border-red-300';
    if (c.includes('preco')) return 'bg-cyan-100 text-cyan-800 border-cyan-300';

    return 'bg-slate-100 text-slate-700 border-slate-300';
  };

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle>Lista de Reclamações</CardTitle>
        <div className="flex gap-4 mt-4">
          <Input
            placeholder="Buscar por título, texto ou usuário..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm"
          />
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filtrar por status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os status</SelectItem>
              {statuses.map((status: any) => (
                <SelectItem key={status} value={status}>{status}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filtrar por categoria" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas as categorias</SelectItem>
              {categories.map((category: any) => (
                <SelectItem key={category} value={category}>{category}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-sm text-muted-foreground mb-4">
          Exibindo {filteredComplaints.length} de {complaints.length} reclamações
        </div>
        <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[60px]">ID</TableHead>
                <TableHead>Título</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Localização</TableHead>
                <TableHead>Usuário</TableHead>
                <TableHead>Data</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredComplaints.map((complaint: any) => (
                <TableRow key={complaint.id}>
                  <TableCell className="font-medium">{complaint.id}</TableCell>
                  <TableCell className="max-w-md">
                    <div className="truncate" title={complaint.title}>
                      {complaint.title}
                    </div>
                  </TableCell>
                  <TableCell>
                    {(() => {
                      const category = getCategory(complaint);
                      return category ? (
                        <Badge variant="outline" className={getCategoryBadgeColor(category)}>
                          {category}
                        </Badge>
                      ) : (
                        <span className="text-sm text-muted-foreground">-</span>
                      );
                    })()}
                  </TableCell>
                  <TableCell>
                    <Badge className={`${getStatusBadgeColor(complaint.status)} font-medium`}>
                      {complaint.status || 'N/A'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {complaint.location || 'N/A'}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {complaint.user_name || 'Anônimo'}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {complaint.complaint_date ? new Date(complaint.complaint_date).toLocaleDateString('pt-BR') : 'N/A'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
