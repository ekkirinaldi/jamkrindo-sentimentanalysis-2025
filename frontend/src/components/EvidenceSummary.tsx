/**
 * Evidence summary component.
 * Shows quick overview of all collected evidence.
 * All text in Bahasa Indonesia.
 */

'use client';

import { CompanyAnalysisResult } from '@/lib/types';
import clsx from 'clsx';

interface Props {
  result: CompanyAnalysisResult;
}

export const EvidenceSummary: React.FC<Props> = ({ result }) => {
  const { analysis } = result;
  const { risk_assessment, sentiment_analysis, legal_records, news_analysis } = analysis;

  const getRiskColor = (level: string): string => {
    const colors = {
      'HIJAU': 'bg-green-100 text-green-800 border-green-300',
      'KUNING': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'MERAH': 'bg-red-100 text-red-800 border-red-300',
    };
    return colors[level as keyof typeof colors] || colors['KUNING'];
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm">
      <h3 className="font-semibold text-lg mb-4 text-gray-900">Ringkasan Bukti</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* News Evidence */}
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">📰</span>
            <h4 className="font-semibold text-sm text-gray-900">Berita</h4>
          </div>
          {news_analysis ? (
            <div className="space-y-1">
              <p className="text-2xl font-bold text-gray-900">
                {news_analysis.total_articles}
              </p>
              <p className="text-xs text-gray-800">
                {news_analysis.positive_count} positif, {news_analysis.negative_count} negatif
              </p>
            </div>
          ) : (
            <p className="text-sm text-gray-900 font-medium">Tidak tersedia</p>
          )}
        </div>

        {/* Legal Evidence */}
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">⚖️</span>
            <h4 className="font-semibold text-sm text-gray-900">Kasus Hukum</h4>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold text-gray-900">
              {legal_records.cases_found || 0}
            </p>
            <p className="text-xs text-gray-800">
              Keparahan: {legal_records.max_severity || 'tidak ada'}
            </p>
          </div>
        </div>

        {/* Sentiment Evidence */}
        <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">💭</span>
            <h4 className="font-semibold text-sm text-gray-900">Sentimen</h4>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold text-gray-900">
              {sentiment_analysis.positive_count}
            </p>
            <p className="text-xs text-gray-800">
              Positif dari {sentiment_analysis.valid_analyses} analisis
            </p>
          </div>
        </div>

        {/* Risk Level */}
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🎯</span>
            <h4 className="font-semibold text-sm text-gray-900">Tingkat Risiko</h4>
          </div>
          <div className="space-y-1">
            <span
              className={clsx(
                'inline-block px-3 py-1 rounded-full text-sm font-bold border',
                getRiskColor(risk_assessment.risk_level)
              )}
            >
              {risk_assessment.risk_level}
            </span>
            <p className="text-xs text-gray-800 mt-1">
              Skor: {risk_assessment.risk_score.toFixed(1)}/100
            </p>
          </div>
        </div>
      </div>

      {/* Key Findings */}
      <div className="mt-6 pt-4 border-t">
        <h4 className="font-semibold text-sm mb-2 text-gray-900">Temuan Utama:</h4>
        <ul className="space-y-1 text-sm text-gray-800">
          {news_analysis && news_analysis.total_articles > 0 && (
            <li>
              • Ditemukan {news_analysis.total_articles} berita terbaru
              {news_analysis.positive_count > news_analysis.negative_count
                ? ' dengan sentimen mayoritas positif'
                : news_analysis.negative_count > news_analysis.positive_count
                ? ' dengan sentimen mayoritas negatif'
                : ' dengan sentimen campuran'}
            </li>
          )}
          {legal_records.cases_found > 0 && (
            <li>
              • Ditemukan {legal_records.cases_found} kasus hukum
              {legal_records.max_severity === 'tinggi' && ' dengan tingkat keparahan tinggi'}
            </li>
          )}
          <li>
            • Analisis sentimen menunjukkan{' '}
            {sentiment_analysis.average_score >= 0.6
              ? 'sentimen positif'
              : sentiment_analysis.average_score <= 0.4
              ? 'sentimen negatif'
              : 'sentimen netral'}{' '}
            (skor: {sentiment_analysis.average_score.toFixed(2)})
          </li>
        </ul>
      </div>
    </div>
  );
};

