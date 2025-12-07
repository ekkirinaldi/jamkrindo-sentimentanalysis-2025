/**
 * Results chart component with pie and bar charts.
 * Chart titles and labels in Bahasa Indonesia.
 */

'use client';

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
    { name: 'Positif', value: sentiment.positive_count },
    { name: 'Netral', value: sentiment.neutral_count },
    { name: 'Negatif', value: sentiment.negative_count },
  ];

  const COLORS = ['#10b981', '#f3f4f6', '#ef4444'];

  const riskData = [
    { name: 'Sentimen', value: risk.sentiment_component },
    { name: 'Mentions', value: risk.mentions_component },
    { name: 'Hukum', value: risk.legal_component },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white p-6 rounded-lg border">
        <h4 className="font-semibold mb-4 text-gray-900">Distribusi Sentimen</h4>
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
        <h4 className="font-semibold mb-4 text-gray-900">Rincian Komponen Risiko</h4>
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

