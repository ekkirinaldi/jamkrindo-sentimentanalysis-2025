/**
 * Source citations component.
 * Displays all source URLs organized by type.
 * All text in Bahasa Indonesia.
 */

'use client';

import { NewsArticle, LegalCase } from '@/lib/types';
import { useState } from 'react';

interface Props {
  perplexitySources?: string[];
  perplexityNewsSources?: string[];
  newsArticles?: NewsArticle[];
  legalCases?: LegalCase[];
}

export const SourceCitations: React.FC<Props> = ({
  perplexitySources = [],
  perplexityNewsSources = [],
  newsArticles = [],
  legalCases = [],
}) => {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  // Combine all Perplexity sources (from company search and news search)
  const allPerplexitySources = [
    ...perplexitySources,
    ...perplexityNewsSources.filter(url => !perplexitySources.includes(url))
  ];

  const hasAnySources =
    allPerplexitySources.length > 0 ||
    newsArticles.length > 0 ||
    legalCases.length > 0;

  if (!hasAnySources) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="font-semibold text-lg mb-2 text-gray-900">Sumber & Referensi</h3>
        <p className="text-gray-800 text-sm">Tidak ada sumber yang tersedia.</p>
      </div>
    );
  }

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-lg text-gray-900">Sumber & Referensi</h3>

      {/* Perplexity Sources - All References */}
      {allPerplexitySources.length > 0 && (
        <div className="border rounded-lg">
          <button
            onClick={() => toggleSection('perplexity')}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">🔍</span>
              <span className="font-medium">
                Referensi Perplexity - Semua Sumber ({allPerplexitySources.length})
              </span>
            </div>
            <span className="text-gray-700">
              {expandedSection === 'perplexity' ? '▼' : '▶'}
            </span>
          </button>
          {expandedSection === 'perplexity' && (
            <div className="px-4 pb-4 space-y-3">
              <p className="text-sm text-gray-800 mb-3">
                Daftar lengkap semua referensi dan sumber berita yang digunakan Perplexity untuk analisis:
              </p>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {allPerplexitySources.map((url, index) => (
                  <div key={index} className="flex items-start gap-2 p-2 hover:bg-gray-50 rounded">
                    <span className="text-sm text-gray-700 min-w-[30px] font-semibold">
                      {index + 1}.
                    </span>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 text-sm text-blue-600 hover:text-blue-800 hover:underline break-all"
                      title={url}
                    >
                      {url}
                    </a>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-700 mt-3 pt-3 border-t">
                💡 Klik pada URL untuk membuka sumber referensi di tab baru
              </p>
            </div>
          )}
        </div>
      )}

      {/* News Article Sources */}
      {newsArticles.length > 0 && (
        <div className="border rounded-lg">
          <button
            onClick={() => toggleSection('news')}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">📰</span>
              <span className="font-medium">Sumber Berita ({newsArticles.length})</span>
            </div>
            <span className="text-gray-700">
              {expandedSection === 'news' ? '▼' : '▶'}
            </span>
          </button>
          {expandedSection === 'news' && (
            <div className="px-4 pb-4 space-y-2">
              {newsArticles
                .filter((article) => article.source_url)
                .map((article, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <span className="text-sm text-gray-700 min-w-[20px]">
                      {index + 1}.
                    </span>
                    <div className="flex-1 min-w-0">
                      <a
                        href={article.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-sm text-blue-600 hover:text-blue-800 hover:underline truncate"
                        title={article.source_url}
                      >
                        {article.title}
                      </a>
                      <p className="text-xs text-gray-700 truncate mt-1">
                        {article.source_url}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}

      {/* Legal Case Sources */}
      {legalCases.length > 0 && (
        <div className="border rounded-lg">
          <button
            onClick={() => toggleSection('legal')}
            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">⚖️</span>
              <span className="font-medium">Dokumen Kasus Hukum ({legalCases.length})</span>
            </div>
            <span className="text-gray-700">
              {expandedSection === 'legal' ? '▼' : '▶'}
            </span>
          </button>
          {expandedSection === 'legal' && (
            <div className="px-4 pb-4 space-y-2">
              {legalCases
                .filter((caseData) => caseData.source_url)
                .map((caseData, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <span className="text-sm text-gray-700 min-w-[20px]">
                      {index + 1}.
                    </span>
                    <div className="flex-1 min-w-0">
                      <a
                        href={caseData.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-sm text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {caseData.case_number}
                      </a>
                      {caseData.case_title && (
                        <p className="text-xs text-gray-800 mt-1 line-clamp-2">
                          {caseData.case_title}
                        </p>
                      )}
                      <p className="text-xs text-gray-700 truncate mt-1">
                        {caseData.source_url}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

