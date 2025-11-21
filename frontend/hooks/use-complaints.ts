'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { complaintsAPI, responsesAPI } from '@/lib/api';

export function useComplaints(filters?: { sentiment?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ['complaints', filters],
    queryFn: () => complaintsAPI.list(filters),
  });
}

export function useComplaint(id: number) {
  return useQuery({
    queryKey: ['complaint', id],
    queryFn: () => complaintsAPI.get(id),
    enabled: !!id,
  });
}

export function useGenerateResponse(complaintId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => responsesAPI.generate(complaintId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['complaints'] });
      queryClient.invalidateQueries({ queryKey: ['complaint', complaintId] });
    },
  });
}

export function useEditResponse(responseId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (text: string) => responsesAPI.edit(responseId, text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['response', responseId] });
    },
  });
}
