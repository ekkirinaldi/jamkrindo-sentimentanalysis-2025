# Frontend Technical Specifications

## 1. Project Dependencies

### Node.js & NPM
```
Node.js: 18+
npm: 9.0+
```

### Package Versions
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "^15.0.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "tailwindcss": "^3.4.0",
    "clsx": "^2.0.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.2",
    "@types/react": "^18.2.0",
    "@types/node": "^20.0.0"
  }
}
```

---

## 2. Frontend Project Structure

```
frontend/
├── package.json                     # Dependencies
├── tsconfig.json                    # TypeScript config
├── next.config.js                   # Next.js config
├── tailwind.config.js               # Tailwind config
├── .env.local.example               # Template
├── Dockerfile                       # Container definition
│
├── public/
│   ├── favicon.ico
│   └── logo.png
│
├── src/
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home page
│   │   └── globals.css              # Global styles
│   │
│   ├── components/
│   │   ├── CompanySearchForm.tsx   # Input form
│   │   ├── RiskScoreBadge.tsx      # Risk display
│   │   ├── ResultsChart.tsx        # Charts (pie + bar)
│   │   ├── LegalRecordsTable.tsx   # Cases table
│   │   └── AnalysisLoader.tsx      # Loading spinner
│   │
│   ├── hooks/
│   │   └── useAnalysis.ts          # Analysis state hook
│   │
│   ├── lib/
│   │   ├── api.ts                  # Axios client
│   │   └── types.ts                # TypeScript types
│   │
│   └── config/
│       └── constants.ts            # API URLs
│
└── tests/
    └── components.test.tsx
```

---

## 3. Core Type Definitions

```typescript
// src/lib/types.ts

export type RiskLevel = "GREEN" | "YELLOW" | "RED";
export type SentimentLabel = "POSITIVE" | "NEUTRAL" | "NEGATIVE";

export interface SentimentScore {
  vader_scores: {
    compound: number;
    positive: number;
    negative: number;
    neutral: number;
  };
  transformer_scores: {
    label: string;
    score: number;
    confidence: number;
  };
  consensus_score: number;
  sentiment_label: SentimentLabel;
  confidence: number;
  text_length: number;
}

export interface SentimentAnalysis {
  total_texts: number;
  valid_analyses: number;
  average_score: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  details: SentimentScore[];
}

export interface LegalCase {
  case_number: string;
  case_date: string;
  case_title: string;
  case_type: string;
  verdict_summary: string;
  severity: "high" | "medium" | "low";
  source_url: string;
}

export interface LegalRecords {
  company_name: string;
  cases_found: number;
  cases: LegalCase[];
  max_severity: string;
  timestamp: string;
}

export interface RiskAssessment {
  risk_score: number;
  risk_level: RiskLevel;
  sentiment_component: number;
  mentions_component: number;
  legal_component: number;
  details: {
    total_texts_analyzed: number;
    positive_texts: number;
    negative_texts: number;
    legal_cases_found: number;
    max_case_severity: string;
  };
  recommendation: string;
}

export interface CompanyAnalysisResult {
  company_name: string;
  status: "success" | "error";
  analysis: {
    risk_assessment: RiskAssessment;
    sentiment_analysis: SentimentAnalysis;
    legal_records: LegalRecords;
  };
  timestamp: string;
  error?: string;
}

export interface AnalysisState {
  isLoading: boolean;
  result: CompanyAnalysisResult | null;
  error: string | null;
  history: CompanyAnalysisResult[];
}
```

---

## 4. API Client Implementation

```typescript
// src/lib/api.ts

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
        throw new Error(
          error.response?.data?.detail || 
          error.message || 
          'Failed to analyze company'
        );
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
```

---

## 5. Custom Hook for Analysis

```typescript
// src/hooks/useAnalysis.ts

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
        error: 'Please enter a company name',
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
        error instanceof Error ? error.message : 'Analysis failed';

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
```

---

## 6. Component Implementations

### CompanySearchForm

```typescript
// src/components/CompanySearchForm.tsx

import { FormEvent, useState } from 'react';

interface Props {
  onSubmit: (ptName: string) => void;
  isLoading: boolean;
}

export const CompanySearchForm: React.FC<Props> = ({ onSubmit, isLoading }) => {
  const [ptName, setPtName] = useState('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(ptName.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Enter company name (e.g., PT Maju Jaya)"
          value={ptName}
          onChange={(e) => setPtName(e.target.value)}
          disabled={isLoading}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={isLoading || !ptName.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
    </form>
  );
};
```

### RiskScoreBadge

```typescript
// src/components/RiskScoreBadge.tsx

import { RiskLevel, RiskAssessment } from '@/lib/types';
import clsx from 'clsx';

interface Props {
  assessment: RiskAssessment;
}

export const RiskScoreBadge: React.FC<Props> = ({ assessment }) => {
  const getRiskColor = (level: RiskLevel): string => ({
    GREEN: 'bg-green-100 border-green-300 text-green-800',
    YELLOW: 'bg-yellow-100 border-yellow-300 text-yellow-800',
    RED: 'bg-red-100 border-red-300 text-red-800',
  }[level]);

  const getRiskEmoji = (level: RiskLevel): string => ({
    GREEN: '✅',
    YELLOW: '⚠️',
    RED: '❌',
  }[level]);

  return (
    <div className="space-y-4">
      <div className={clsx('p-6 rounded-lg border-2', getRiskColor(assessment.risk_level))}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">Risk Score</h3>
            <p className="text-sm opacity-75">Overall Assessment</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{assessment.risk_score}/100</div>
            <div className="text-2xl">{getRiskEmoji(assessment.risk_level)}</div>
          </div>
        </div>
        <p className="mt-4 text-sm font-medium italic">{assessment.recommendation}</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <ComponentScore label="Sentiment" score={assessment.sentiment_component} weight="30%" />
        <ComponentScore label="Mentions" score={assessment.mentions_component} weight="30%" />
        <ComponentScore label="Legal" score={assessment.legal_component} weight="40%" />
      </div>
    </div>
  );
};

const ComponentScore: React.FC<{ label: string; score: number; weight: string }> = 
  ({ label, score, weight }) => (
    <div className="p-4 border rounded-lg bg-gray-50">
      <p className="text-xs font-semibold text-gray-600">{label}</p>
      <p className="text-2xl font-bold mt-1">{score}</p>
      <p className="text-xs text-gray-500 mt-1">Weight: {weight}</p>
    </div>
  );
```

### ResultsChart

```typescript
// src/components/ResultsChart.tsx

import { SentimentAnalysis, RiskAssessment } from '@/lib/types';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';

interface Props {
  sentiment: SentimentAnalysis;
  risk: RiskAssessment;
}

export const ResultsChart: React.FC<Props> = ({ sentiment, risk }) => {
  const sentimentData = [
    { name: 'Positive', value: sentiment.positive_count },
    { name: 'Neutral', value: sentiment.neutral_count },
    { name: 'Negative', value: sentiment.negative_count },
  ];

  const COLORS = ['#10b981', '#f3f4f6', '#ef4444'];

  const riskData = [
    { name: 'Sentiment', value: risk.sentiment_component },
    { name: 'Mentions', value: risk.mentions_component },
    { name: 'Legal', value: risk.legal_component },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white p-6 rounded-lg border">
        <h4 className="font-semibold mb-4">Sentiment Distribution</h4>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={sentimentData} cx="50%" cy="50%" outerRadius={100} dataKey="value">
              {sentimentData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white p-6 rounded-lg border">
        <h4 className="font-semibold mb-4">Risk Component Breakdown</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={riskData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip formatter={(v) => `${v}/100`} />
            <Bar dataKey="value" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
```

### LegalRecordsTable

```typescript
// src/components/LegalRecordsTable.tsx

import { LegalRecords } from '@/lib/types';
import clsx from 'clsx';

interface Props {
  records: LegalRecords;
}

export const LegalRecordsTable: React.FC<Props> = ({ records }) => {
  if (records.cases_found === 0) {
    return (
      <div className="p-6 bg-green-50 rounded-lg border border-green-200">
        <p className="text-green-800">✅ No legal records found. Clean legal history.</p>
      </div>
    );
  }

  const getSeverityColor = (severity: string): string => ({
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-blue-100 text-blue-800',
  }[severity] || 'bg-gray-100 text-gray-800');

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-lg">Legal Records Found: {records.cases_found}</h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-4 py-2 text-left font-semibold">Case Number</th>
              <th className="px-4 py-2 text-left font-semibold">Date</th>
              <th className="px-4 py-2 text-left font-semibold">Type</th>
              <th className="px-4 py-2 text-left font-semibold">Severity</th>
            </tr>
          </thead>
          <tbody>
            {records.cases.map((c, i) => (
              <tr key={i} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-xs">{c.case_number}</td>
                <td className="px-4 py-3">{c.case_date}</td>
                <td className="px-4 py-3">{c.case_type}</td>
                <td className="px-4 py-3">
                  <span className={clsx('px-3 py-1 rounded-full text-xs font-semibold', getSeverityColor(c.severity))}>
                    {c.severity.toUpperCase()}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

### AnalysisLoader

```typescript
// src/components/AnalysisLoader.tsx

export const AnalysisLoader: React.FC = () => (
  <div className="flex justify-center py-12">
    <div className="text-center">
      <div className="inline-block">
        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
      </div>
      <p className="mt-4 text-gray-600">Analyzing company data...</p>
      <p className="text-xs text-gray-500 mt-2">This may take 15-30 seconds</p>
    </div>
  </div>
);
```

---

## 7. Main Page Layout

```typescript
// src/app/page.tsx

'use client';

import { CompanySearchForm } from '@/components/CompanySearchForm';
import { RiskScoreBadge } from '@/components/RiskScoreBadge';
import { ResultsChart } from '@/components/ResultsChart';
import { LegalRecordsTable } from '@/components/LegalRecordsTable';
import { AnalysisLoader } from '@/components/AnalysisLoader';
import { useAnalysis } from '@/hooks/useAnalysis';

export default function Home() {
  const { isLoading, result, error, analyzeCompany, clearResult } = useAnalysis();

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Credit Scoring Analysis</h1>
          <p className="text-gray-600 mt-1">Sentiment analysis & legal record review</p>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex justify-center mb-12">
          <CompanySearchForm onSubmit={analyzeCompany} isLoading={isLoading} />
        </div>

        {isLoading && <AnalysisLoader />}

        {error && (
          <div className="max-w-2xl mx-auto mb-8 p-4 bg-red-100 border border-red-300 rounded-lg text-red-800">
            <p className="font-semibold">Analysis Failed</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {result && !isLoading && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">{result.company_name}</h2>
              <p className="text-gray-600 text-sm mt-1">
                Completed at {new Date(result.timestamp).toLocaleString()}
              </p>
            </div>

            <RiskScoreBadge assessment={result.analysis.risk_assessment} />

            <div className="bg-white p-6 rounded-lg border">
              <ResultsChart
                sentiment={result.analysis.sentiment_analysis}
                risk={result.analysis.risk_assessment}
              />
            </div>

            <div className="bg-white p-6 rounded-lg border">
              <LegalRecordsTable records={result.analysis.legal_records} />
            </div>

            <div className="flex gap-4 justify-center">
              <button
                onClick={clearResult}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-semibold"
              >
                New Search
              </button>
              <button
                onClick={() => {
                  const element = document.createElement('a');
                  element.setAttribute(
                    'href',
                    'data:text/plain;charset=utf-8,' +
                      encodeURIComponent(JSON.stringify(result, null, 2))
                  );
                  element.setAttribute('download', `${result.company_name}-analysis.json`);
                  element.style.display = 'none';
                  document.body.appendChild(element);
                  element.click();
                  document.body.removeChild(element);
                }}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
              >
                Export Results
              </button>
            </div>
          </div>
        )}

        {!result && !isLoading && !error && (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">Enter a company name above to begin</p>
          </div>
        )}
      </div>
    </main>
  );
}
```

---

## 8. Global Styles

```css
/* src/app/globals.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color-scheme: light;
}

body {
  background: #f9fafb;
}

@media (prefers-color-scheme: dark) {
  html {
    color-scheme: dark;
  }
  body {
    background: #111827;
  }
}
```

---

## 9. TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 10. Next.js Configuration

```javascript
// next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
```

---

## 11. Tailwind Configuration

```javascript
// tailwind.config.js

module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

---

## 12. Environment Configuration

```bash
# .env.local.example

NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 13. Docker Build

```dockerfile
# Dockerfile (Production)

FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./

EXPOSE 3000

CMD ["npm", "start"]
```

---

## 14. Build & Run Commands

```bash
# Development
npm install
npm run dev
# Runs on http://localhost:3000

# Production build
npm run build
npm start

# Docker build
docker build -t sa-frontend:latest .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000 sa-frontend:latest
```

---

## 15. Component Communication Flow

```
Home (page.tsx)
  ├── useAnalysis hook
  │   └── apiClient.analyzeCompany(ptName)
  │       └── POST /api/v1/company/analyze
  │
  ├── CompanySearchForm
  │   └── Calls: analyzeCompany(ptName)
  │
  ├── AnalysisLoader
  │   └── Shows: isLoading state
  │
  ├── RiskScoreBadge
  │   └── Receives: result.analysis.risk_assessment
  │
  ├── ResultsChart
  │   └── Receives: sentiment + risk data
  │
  └── LegalRecordsTable
      └── Receives: result.analysis.legal_records
```

---

## 16. Data Flow

```
User Input (PT name)
  ↓
CompanySearchForm validates
  ↓
useAnalysis.analyzeCompany(ptName)
  ↓
APIClient.post(/api/v1/company/analyze)
  ↓
Backend processes (15-30 sec)
  ↓
Response: CompanyAnalysisResult
  ↓
setState in useAnalysis hook
  ↓
Re-render with result
  ↓
Display: RiskScoreBadge, Charts, LegalRecords
```

---

## 17. Browser Compatibility

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Requires: JavaScript enabled

---

## 18. Performance Targets

- Initial page load: < 3 seconds
- Analysis request: 15-30 seconds (backend dependent)
- Chart rendering: < 500ms
- Export JSON: < 100ms
- Bundle size: < 300KB (gzipped)

---

## 19. Error Handling

```typescript
// Common error scenarios

// 1. Backend connection failure
try {
  const result = await apiClient.analyzeCompany(ptName);
} catch (error) {
  setState(...{ error: 'Backend service unavailable' });
}

// 2. API validation error
// Backend returns 400 with error message
// Caught and displayed in UI

// 3. Timeout (>120 seconds)
// Axios timeout triggers catch block
// User sees: "Request timed out"

// 4. Empty results
// Handled gracefully with empty state message
```

---

## 20. Deployment Notes

### Docker
- Build: `docker build -t sa-frontend .`
- Run: `docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=... sa-frontend`
- Port: 3000 (internal, exposed via Nginx)

### Production Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend API endpoint (required)
- `NODE_ENV`: set to production automatically by Next.js

### Production Build
```bash
npm run build     # Optimized output to .next/
npm start         # Runs Next.js server (not dev server)
```
