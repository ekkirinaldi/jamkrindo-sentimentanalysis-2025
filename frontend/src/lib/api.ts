/**
 * API client with Axios.
 * Error messages in Bahasa Indonesia.
 */

import axios, { AxiosInstance } from 'axios';
import { CompanyAnalysisResult } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000,  // 2 minute timeout
    });
  }

  async analyzeCompany(ptName: string, detailed = false): Promise<CompanyAnalysisResult> {
    try {
      const response = await this.client.post('/api/v1/company/analyze', {
        pt_name: ptName,
        detailed,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = 
          error.response?.data?.detail || 
          error.message || 
          'Gagal menganalisis perusahaan';
        throw new Error(errorMessage);
      }
      throw error;
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

export const apiClient = new APIClient();

