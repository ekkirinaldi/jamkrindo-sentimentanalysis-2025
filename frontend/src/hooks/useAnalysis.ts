/**
 * Custom hook for analysis state management.
 * Validation messages in Bahasa Indonesia.
 */

import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api';
import { CompanyAnalysisResult, AnalysisState } from '@/lib/types';

export const useAnalysis = () => {
  const [state, setState] = useState<AnalysisState>({
    isLoading: false,
    result: null,
    error: null,
    history: [],
  });

  const analyzeCompany = useCallback(async (ptName: string) => {
    if (!ptName.trim()) {
      setState(prev => ({
        ...prev,
        error: 'Mohon masukkan nama perusahaan',
      }));
      return;
    }

    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    try {
      const result = await apiClient.analyzeCompany(ptName, false);

      setState(prev => ({
        ...prev,
        result,
        isLoading: false,
        history: [result, ...prev.history].slice(0, 10),
      }));
    } catch (error) {
      const errorMessage = 
        error instanceof Error ? error.message : 'Analisis gagal';

      setState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
      }));
    }
  }, []);

  const clearResult = useCallback(() => {
    setState(prev => ({
      ...prev,
      result: null,
      error: null,
    }));
  }, []);

  return {
    ...state,
    analyzeCompany,
    clearResult,
  };
};

