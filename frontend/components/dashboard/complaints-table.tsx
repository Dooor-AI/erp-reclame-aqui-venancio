'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useQuery } from '@tanstack/react-query';
import { complaintsAPI } from '@/lib/api';

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
          <CardTitle>Lista de Reclamações</CardTitle>
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
          <CardTitle>Lista de Reclamações</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  // Extract unique statuses and categories
  const statuses = Array.from(new Set(complaints.map((c: any) => c.status).filter(Boolean)));
  const categories = Array.from(new Set(complaints.map((c: any) => c.category).filter(Boolean)));

  // Filter complaints
  const filteredComplaints = complaints.filter((complaint: any) => {
    const matchesSearch = searchTerm === '' ||
      complaint.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      complaint.text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      complaint.user_name?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'all' || complaint.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || complaint.category === categoryFilter;

    return matchesSearch && matchesStatus && matchesCategory;
  });

  const getStatusBadgeColor = (status: string) => {
    if (status?.includes('Resolvido')) return 'bg-green-100 text-green-800';
    if (status?.includes('Respondida')) return 'bg-blue-100 text-blue-800';
    if (status?.includes('réplica')) return 'bg-yellow-100 text-yellow-800';
    if (status?.includes('Não')) return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
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
                    <Badge variant="outline">
                      {complaint.category || 'N/A'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusBadgeColor(complaint.status)}>
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
