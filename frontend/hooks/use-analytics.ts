'use client';

import { useQuery } from '@tanstack/react-query';
import { complaintsAPI, analyticsAPI } from '@/lib/api';

export function useComplaintStats() {
  return useQuery({
    queryKey: ['complaint-stats'],
    queryFn: () => complaintsAPI.stats(),
  });
}

export function useSentimentStats() {
  return useQuery({
    queryKey: ['sentiment-stats'],
    queryFn: () => analyticsAPI.sentimentStats(),
  });
}

export function useCategoryStats() {
  return useQuery({
    queryKey: ['category-stats'],
    queryFn: () => analyticsAPI.categoryStats(),
  });
}

export function useUrgencyStats() {
  return useQuery({
    queryKey: ['urgency-stats'],
    queryFn: () => analyticsAPI.urgencyStats(),
  });
}

export function useTimelineStats(days = 30) {
  return useQuery({
    queryKey: ['timeline-stats', days],
    queryFn: () => analyticsAPI.timelineStats(days),
  });
}

export function useLocationStats(limit = 20) {
  return useQuery({
    queryKey: ['location-stats', limit],
    queryFn: () => analyticsAPI.locationStats(limit),
  });
}

export function useStoreTypeStats() {
  return useQuery({
    queryKey: ['store-type-stats'],
    queryFn: () => analyticsAPI.storeTypeStats(),
  });
}

export function useTagStats(limit = 30) {
  return useQuery({
    queryKey: ['tag-stats', limit],
    queryFn: () => analyticsAPI.tagStats(limit),
  });
}

export function useWeeklyTrends() {
  return useQuery({
    queryKey: ['weekly-trends'],
    queryFn: () => analyticsAPI.weeklyTrends(),
  });
}

export function useResponseMetrics() {
  return useQuery({
    queryKey: ['response-metrics'],
    queryFn: () => analyticsAPI.responseMetrics(),
  });
}
