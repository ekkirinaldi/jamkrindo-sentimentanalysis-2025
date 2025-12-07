/**
 * Main page with all components integrated.
 * All UI text in Bahasa Indonesia.
 */

'use client';

import { CompanySearchForm } from '@/components/CompanySearchForm';
import { RiskScoreBadge } from '@/components/RiskScoreBadge';
import { ResultsChart } from '@/components/ResultsChart';
import { LegalRecordsTable } from '@/components/LegalRecordsTable';
import { NewsArticlesList } from '@/components/NewsArticlesList';
import { EvidenceSummary } from '@/components/EvidenceSummary';
import { SourceCitations } from '@/components/SourceCitations';
import { AnalysisLoader } from '@/components/AnalysisLoader';
import { useAnalysis } from '@/hooks/useAnalysis';

export default function Home() {
  const { isLoading, result, error, analyzeCompany, clearResult } = useAnalysis();

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Analisis Penilaian Kredit</h1>
          <p className="text-gray-700 mt-1">Analisis sentimen & tinjauan catatan hukum</p>
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
            <p className="font-semibold">Analisis Gagal</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {result && !isLoading && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">{result.company_name}</h2>
              <p className="text-gray-700 text-sm mt-1">
                Selesai pada {new Date(result.timestamp).toLocaleString('id-ID')}
              </p>
            </div>

            <RiskScoreBadge assessment={result.analysis.risk_assessment} />

            {/* Evidence Summary */}
            <EvidenceSummary result={result} />

            {/* News Articles */}
            <div className="bg-white p-6 rounded-lg border">
              <NewsArticlesList newsAnalysis={result.analysis.news_analysis} />
            </div>

            {/* Legal Records */}
            <div className="bg-white p-6 rounded-lg border">
              <LegalRecordsTable records={result.analysis.legal_records} />
            </div>

            {/* Charts */}
            <div className="bg-white p-6 rounded-lg border">
              <ResultsChart
                sentiment={result.analysis.sentiment_analysis}
                risk={result.analysis.risk_assessment}
              />
            </div>

            {/* Source Citations */}
            <div className="bg-white p-6 rounded-lg border">
              <SourceCitations
                perplexitySources={result.analysis.perplexity_sources}
                perplexityNewsSources={result.analysis.perplexity_news_sources}
                newsArticles={result.analysis.news_analysis?.articles}
                legalCases={result.analysis.legal_records.cases}
              />
            </div>

            <div className="flex gap-4 justify-center">
              <button
                onClick={clearResult}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-semibold"
              >
                Pencarian Baru
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
                Ekspor Hasil
              </button>
            </div>
          </div>
        )}

        {!result && !isLoading && !error && (
          <div className="text-center py-12">
            <p className="text-gray-800 text-lg">Masukkan nama perusahaan di atas untuk memulai</p>
          </div>
        )}
      </div>
    </main>
  );
}

