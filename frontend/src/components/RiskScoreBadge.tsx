/**
 * Risk score badge component.
 * Displays risk levels in Bahasa Indonesia: HIJAU, KUNING, MERAH
 */

'use client';

import { RiskLevel, RiskAssessment } from '@/lib/types';
import clsx from 'clsx';

interface Props {
  assessment: RiskAssessment;
}

export const RiskScoreBadge: React.FC<Props> = ({ assessment }) => {
  const getRiskColor = (level: RiskLevel): string => ({
    HIJAU: 'bg-green-100 border-green-300 text-green-900',
    KUNING: 'bg-yellow-100 border-yellow-300 text-yellow-900',
    MERAH: 'bg-red-100 border-red-300 text-red-900',
  }[level]);

  const getRiskEmoji = (level: RiskLevel): string => ({
    HIJAU: '✅',
    KUNING: '⚠️',
    MERAH: '❌',
  }[level]);

  return (
    <div className="space-y-4">
      <div className={clsx('p-6 rounded-lg border-2', getRiskColor(assessment.risk_level))}>
        <div className="flex items-center justify-between">
          <div className="text-gray-900">
            <h3 className="text-lg font-semibold text-gray-900">Skor Risiko</h3>
            <p className="text-sm text-gray-900">Penilaian Keseluruhan</p>
          </div>
          <div className="text-right text-gray-900">
            <div className="text-4xl font-bold text-gray-900">{assessment.risk_score}/100</div>
            <div className="text-2xl">{getRiskEmoji(assessment.risk_level)}</div>
          </div>
        </div>
        <p className="mt-4 text-sm font-medium italic text-gray-900">{assessment.recommendation}</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <ComponentScore label="Sentimen" score={assessment.sentiment_component} weight="30%" />
        <ComponentScore label="Mentions" score={assessment.mentions_component} weight="30%" />
        <ComponentScore label="Hukum" score={assessment.legal_component} weight="40%" />
      </div>
    </div>
  );
};

const ComponentScore: React.FC<{ label: string; score: number; weight: string }> = 
  ({ label, score, weight }) => (
    <div className="p-4 border rounded-lg bg-gray-50">
      <p className="text-xs font-semibold text-gray-800">{label}</p>
      <p className="text-2xl font-bold mt-1 text-gray-900">{score}</p>
      <p className="text-xs text-gray-700 mt-1">Bobot: {weight}</p>
    </div>
  );

