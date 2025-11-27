'use client';

import { useQuery } from '@tanstack/react-query';
import { benchmarkAPI } from '@/lib/api';

export function useBenchmarkComparison() {
  return useQuery({
    queryKey: ['benchmark-comparison'],
    queryFn: () => benchmarkAPI.comparison(),
  });
}

export function useBenchmarkCompetitors() {
  return useQuery({
    queryKey: ['benchmark-competitors'],
    queryFn: () => benchmarkAPI.competitors(),
  });
}

export function useBenchmarkBestResponses(params?: { competitor_id?: number; limit?: number }) {
  return useQuery({
    queryKey: ['benchmark-best-responses', params],
    queryFn: () => benchmarkAPI.bestResponses(params),
  });
}

export function useBenchmarkResponsePatterns() {
  return useQuery({
    queryKey: ['benchmark-response-patterns'],
    queryFn: () => benchmarkAPI.responsePatterns(),
  });
}

export function useBenchmarkStats() {
  return useQuery({
    queryKey: ['benchmark-stats'],
    queryFn: () => benchmarkAPI.stats(),
  });
}

export function useCompetitorComplaints(competitorId: number, page = 1, pageSize = 10) {
  return useQuery({
    queryKey: ['competitor-complaints', competitorId, page, pageSize],
    queryFn: () => benchmarkAPI.competitorComplaints(competitorId, page, pageSize),
    enabled: !!competitorId,
  });
}
