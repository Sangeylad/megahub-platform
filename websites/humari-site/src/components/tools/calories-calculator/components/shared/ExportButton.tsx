'use client';

import { useState } from 'react';
import { exportToPDF } from '../../utils/exportPDF';
import type { CalorieCalculatorHook } from '../../types';

interface ExportButtonProps {
  calculator: CalorieCalculatorHook;
}

export function ExportButton({ calculator }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [exportError, setExportError] = useState<string>('');

  const handleExport = async () => {
    if (!calculator.results || isExporting) return;

    setIsExporting(true);
    setExportSuccess(false);
    setExportError('');

    try {
      console.log('🚀 Début export PDF...');
      
      const exportData = calculator.getExportData();
      if (!exportData) {
        throw new Error('Aucune donnée à exporter');
      }

      console.log('📊 Données à exporter:', {
        goal: exportData.userData.goal,
        bmr: exportData.results.bmr,
        tdee: exportData.results.tdee
      });

      await exportToPDF(exportData);
      
      console.log('✅ Export PDF réussi');
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 4000);
      
    } catch (error) {
      console.error('❌ Erreur export PDF:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erreur inconnue';
      setExportError(errorMessage);
      setTimeout(() => setExportError(''), 6000);
    } finally {
      setIsExporting(false);
    }
  };

  if (!calculator.results) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Bouton principal */}
      <button
        onClick={handleExport}
        disabled={isExporting}
        className={`
          group inline-flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300
          ${isExporting
            ? 'bg-neutral-400 text-neutral-200 cursor-not-allowed'
            : exportSuccess
              ? 'bg-green-500 text-white'
              : exportError
                ? 'bg-red-500 text-white'
                : 'bg-brand-500 hover:bg-brand-600 text-white shadow-lg hover:shadow-xl hover:-translate-y-1'
          }
        `}
      >
        {isExporting ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Génération du PDF...
          </>
        ) : exportSuccess ? (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            PDF téléchargé !
          </>
        ) : exportError ? (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            Erreur export
          </>
        ) : (
          <>
            <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Télécharger le PDF
          </>
        )}
      </button>

      {/* Messages d&apos;état */}
      {exportError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <p className="text-red-800 font-medium">❌ Erreur d&apos;export</p>
          <p className="text-red-600 text-sm mt-1">{exportError}</p>
          <button 
            onClick={() => setExportError('')}
            className="text-red-600 text-xs underline mt-2 hover:text-red-800"
          >
            Fermer
          </button>
        </div>
      )}

      {!exportError && !exportSuccess && (
        <div className="text-center">
          <p className="text-sm text-neutral-600 mb-2">
            📄 Rapport complet avec vos résultats personnalisés
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-xs text-neutral-500">
            <span>✅ Calculs détaillés</span>
            <span>✅ Répartition macros</span>
            <span>✅ Recommandations</span>
            <span>✅ 100% gratuit</span>
          </div>
        </div>
      )}

      {/* Debug info en dev */}
      {process.env.NODE_ENV === 'development' && (
        <details className="text-xs text-neutral-500">
          <summary className="cursor-pointer">Debug info</summary>
          <pre className="mt-2 p-2 bg-neutral-100 rounded text-xs overflow-auto">
            {JSON.stringify({
              hasResults: !!calculator.results,
              goal: calculator.userData.goal,
              bmr: calculator.results?.bmr,
              exportData: !!calculator.getExportData()
            }, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}