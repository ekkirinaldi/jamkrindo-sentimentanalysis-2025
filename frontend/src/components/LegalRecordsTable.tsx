/**
 * Legal records table component.
 * Table headers and case types in Bahasa Indonesia.
 */

'use client';

import { LegalRecords, LegalCase } from '@/lib/types';
import clsx from 'clsx';
import { useState } from 'react';

interface Props {
  records: LegalRecords;
}

interface CaseRowProps {
  caseData: LegalCase;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}

const CaseRow: React.FC<CaseRowProps> = ({ caseData, index, isExpanded, onToggle }) => {
  const getSeverityColor = (severity: string): string => ({
    tinggi: 'bg-red-100 text-red-800',
    sedang: 'bg-yellow-100 text-yellow-800',
    rendah: 'bg-blue-100 text-blue-800',
    'tidak ada': 'bg-gray-100 text-gray-800',
  }[severity] || 'bg-gray-100 text-gray-800');

  const getCaseTypeLabel = (caseType: string): string => {
    const mapping: Record<string, string> = {
      'pidana': 'Pidana',
      'perdata': 'Perdata',
      'tata usaha negara': 'Tata Usaha Negara',
      'niaga': 'Niaga',
      'pajak': 'Pajak',
    };
    return mapping[caseType.toLowerCase()] || caseType;
  };

  const getSeverityLabel = (severity: string): string => {
    const mapping: Record<string, string> = {
      'tinggi': 'TINGGI',
      'sedang': 'SEDANG',
      'rendah': 'RENDAH',
      'tidak ada': 'TIDAK ADA',
    };
    return mapping[severity.toLowerCase()] || severity.toUpperCase();
  };

  return (
    <>
      <tr
        className="border-b hover:bg-gray-50 cursor-pointer"
        onClick={onToggle}
      >
        <td className="px-4 py-3 font-mono text-xs">{caseData.case_number}</td>
        <td className="px-4 py-3">{caseData.case_date}</td>
        <td className="px-4 py-3">{getCaseTypeLabel(caseData.case_type)}</td>
        <td className="px-4 py-3">
          <span className={clsx('px-3 py-1 rounded-full text-xs font-semibold', getSeverityColor(caseData.severity))}>
            {getSeverityLabel(caseData.severity)}
          </span>
        </td>
        <td className="px-4 py-3">
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
            {isExpanded ? 'Sembunyikan' : 'Detail'}
          </button>
        </td>
      </tr>
      {isExpanded && (
        <tr className="bg-gray-50">
          <td colSpan={5} className="px-4 py-4">
            <div className="space-y-3">
              {caseData.case_title && (
                <div>
                  <h5 className="font-semibold text-sm mb-1 text-gray-900">Judul Kasus:</h5>
                  <p className="text-sm text-gray-800">{caseData.case_title}</p>
                </div>
              )}
              {caseData.verdict_summary && (
                <div>
                  <h5 className="font-semibold text-sm mb-1 text-gray-900">Ringkasan Putusan:</h5>
                  <p className="text-sm text-gray-800 leading-relaxed">
                    {caseData.verdict_summary}
                  </p>
                </div>
              )}
              {caseData.source_url && (
                <div>
                  <a
                    href={caseData.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Lihat dokumen lengkap →
                  </a>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

export const LegalRecordsTable: React.FC<Props> = ({ records }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  if (records.cases_found === 0) {
    return (
      <div className="p-6 bg-green-50 rounded-lg border border-green-200">
        <p className="text-green-800">✅ Tidak ada catatan hukum ditemukan. Riwayat hukum bersih.</p>
      </div>
    );
  }

  const getSeverityColor = (severity: string): string => ({
    tinggi: 'bg-red-100 text-red-800',
    sedang: 'bg-yellow-100 text-yellow-800',
    rendah: 'bg-blue-100 text-blue-800',
    'tidak ada': 'bg-gray-100 text-gray-800',
  }[severity] || 'bg-gray-100 text-gray-800');

  const getCaseTypeLabel = (caseType: string): string => {
    const mapping: Record<string, string> = {
      'pidana': 'Pidana',
      'perdata': 'Perdata',
      'tata usaha negara': 'Tata Usaha Negara',
      'niaga': 'Niaga',
    };
    return mapping[caseType.toLowerCase()] || caseType;
  };

  const getSeverityLabel = (severity: string): string => {
    const mapping: Record<string, string> = {
      'tinggi': 'TINGGI',
      'sedang': 'SEDANG',
      'rendah': 'RENDAH',
      'tidak ada': 'TIDAK ADA',
    };
    return mapping[severity.toLowerCase()] || severity.toUpperCase();
  };

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-lg text-gray-900">Catatan Hukum Ditemukan: {records.cases_found}</h3>

      {records.error && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 text-sm">⚠️ {records.error}</p>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-4 py-2 text-left font-semibold text-gray-900">Nomor Kasus</th>
              <th className="px-4 py-2 text-left font-semibold text-gray-900">Tanggal</th>
              <th className="px-4 py-2 text-left font-semibold text-gray-900">Jenis</th>
              <th className="px-4 py-2 text-left font-semibold text-gray-900">Tingkat Keparahan</th>
              <th className="px-4 py-2 text-left font-semibold text-gray-900">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {records.cases.map((c, i) => (
              <CaseRow
                key={i}
                caseData={c}
                index={i}
                isExpanded={expandedIndex === i}
                onToggle={() => setExpandedIndex(expandedIndex === i ? null : i)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

