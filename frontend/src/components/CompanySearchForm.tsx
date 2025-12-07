/**
 * Company search form component.
 * All UI text in Bahasa Indonesia.
 */

'use client';

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
          placeholder="Masukkan nama perusahaan (contoh: PT Maju Jaya)"
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
          {isLoading ? 'Menganalisis...' : 'Analisis'}
        </button>
      </div>
    </form>
  );
};

