// src/components/tools/beroas-calculator/components/shared/ExportButton.tsx
'use client';

import { useState } from 'react';
import { exportUtils } from '../../utils/exportUtils';
import type { useBeroasCalculator } from '../../hooks/useBeroasCalculator';

interface ExportButtonProps {
  calculator: ReturnType<typeof useBeroasCalculator>;
}

export function ExportButton({ calculator }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      await exportUtils.exportToPDF(calculator.state, calculator.results);
      
      // Show success toast
      const toast = document.createElement('div');
      toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform';
      toast.textContent = '📊 Rapport exporté avec succès !';
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.classList.remove('translate-x-full');
      }, 100);
      
      setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => document.body.removeChild(toast), 300);
      }, 3000);
      
    } catch (error) {
      console.error('Export error:', error);
      
      // Show error toast
      const toast = document.createElement('div');
      toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      toast.textContent = '❌ Erreur lors de l\'export';
      document.body.appendChild(toast);
      
      setTimeout(() => document.body.removeChild(toast), 3000);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isExporting}
      className={`
        inline-flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg
        transition-all duration-300 shadow-lg
        ${isExporting 
          ? 'bg-neutral-400 cursor-not-allowed' 
          : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 hover:shadow-xl hover:-translate-y-1'
        }
        text-white
      `}
    >
      {isExporting ? (
        <>
          <div className="animate-spin w-5 h-5 border-2 border-white/30 border-t-white rounded-full"></div>
          Génération du PDF...
        </>
      ) : (
        <>
          📊 Exporter mon analyse BEROAS (PDF)
        </>
      )}
    </button>
  );
}