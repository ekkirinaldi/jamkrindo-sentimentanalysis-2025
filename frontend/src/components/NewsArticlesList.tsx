/**
 * News articles list component.
 * Displays news articles with sentiment analysis.
 * All text in Bahasa Indonesia.
 */

'use client';

import { NewsAnalysis } from '@/lib/types';
import { useState } from 'react';
import clsx from 'clsx';

interface Props {
  newsAnalysis?: NewsAnalysis;
}

export const NewsArticlesList: React.FC<Props> = ({ newsAnalysis }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (!newsAnalysis || newsAnalysis.total_articles === 0) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
        <h3 className="font-semibold text-lg mb-2 text-gray-900">Berita Terbaru</h3>
        <p className="text-gray-800">
          {newsAnalysis?.error 
            ? `⚠️ ${newsAnalysis.error}` 
            : 'Tidak ada berita terbaru ditemukan.'}
        </p>
      </div>
    );
  }

  const getSentimentColor = (label: string): string => {
    const colors = {
      'POSITIF': 'bg-green-100 text-green-800 border-green-300',
      'NETRAL': 'bg-gray-100 text-gray-800 border-gray-300',
      'NEGATIF': 'bg-red-100 text-red-800 border-red-300',
    };
    return colors[label as keyof typeof colors] || colors['NETRAL'];
  };

  const getSentimentEmoji = (label: string): string => {
    const emojis = {
      'POSITIF': '✅',
      'NETRAL': '⚠️',
      'NEGATIF': '❌',
    };
    return emojis[label as keyof typeof emojis] || '⚠️';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-lg text-gray-900">Berita Terbaru</h3>
        <div className="flex gap-4 text-sm">
          <span className="text-green-700">
            ✅ {newsAnalysis.positive_count} Positif
          </span>
          <span className="text-gray-700">
            ⚠️ {newsAnalysis.neutral_count} Netral
          </span>
          <span className="text-red-700">
            ❌ {newsAnalysis.negative_count} Negatif
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {newsAnalysis.articles.map((article, index) => (
          <div
            key={index}
            className="bg-white border rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-3">
                    <span
                      className={clsx(
                        'px-3 py-1 rounded-full text-xs font-semibold border',
                        getSentimentColor(article.sentiment_label)
                      )}
                    >
                      {getSentimentEmoji(article.sentiment_label)}{' '}
                      {article.sentiment_label}
                    </span>
                    {article.date && (
                      <span className="text-xs text-gray-600">
                        {article.date}
                      </span>
                    )}
                  </div>
                  
                  {/* Title - Large and Bold */}
                  <h4 className="text-lg font-bold text-gray-900 mb-3 leading-tight">
                    {article.title}
                  </h4>
                  
                  {/* Summary - Smaller and Lighter */}
                  {expandedIndex === index ? (
                    <div className="space-y-3">
                      <div className="bg-gray-50 p-3 rounded border-l-4 border-blue-500">
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {article.summary}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-600 pt-2 border-t">
                        <span className="font-medium">Skor Sentimen: <span className="text-gray-900">{article.sentiment_score.toFixed(3)}</span></span>
                        <span>•</span>
                        <span className="font-medium">Kepercayaan: <span className="text-gray-900">{(article.confidence * 100).toFixed(1)}%</span></span>
                      </div>
                      {article.source_url && (
                        <a
                          href={article.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          Baca artikel lengkap →
                        </a>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">
                        {article.summary}
                      </p>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex items-center gap-3 mt-3 pt-3 border-t">
                {article.source_url ? (
                  <a
                    href={article.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    Baca selengkapnya →
                  </a>
                ) : (
                  <span className="text-sm text-gray-500">Link tidak tersedia</span>
                )}
                <button
                  onClick={() =>
                    setExpandedIndex(expandedIndex === index ? null : index)
                  }
                  className="text-sm text-gray-600 hover:text-gray-800 font-medium"
                >
                  {expandedIndex === index ? 'Sembunyikan detail' : 'Lihat detail'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

