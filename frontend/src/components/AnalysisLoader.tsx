/**
 * Loading spinner component.
 * Loading messages in Bahasa Indonesia.
 */

'use client';

export const AnalysisLoader: React.FC = () => (
  <div className="flex justify-center py-12">
    <div className="text-center">
      <div className="inline-block">
        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
      </div>
      <p className="mt-4 text-gray-800">Menganalisis data perusahaan...</p>
      <p className="text-xs text-gray-700 mt-2">Ini mungkin memakan waktu 15-30 detik</p>
    </div>
  </div>
);

