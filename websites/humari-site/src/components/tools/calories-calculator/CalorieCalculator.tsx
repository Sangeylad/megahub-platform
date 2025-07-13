'use client';

import { Suspense, useEffect } from 'react';
import { useCalorieCalculator } from './hooks/useCalorieCalculator';
import { TabNavigation } from './components/shared/TabNavigation';
import { Calculator } from './components/Calculator';
import { ResultsDisplay } from './components/ResultsDisplay';
import { ExportButton } from './components/shared/ExportButton';
import type { TabType, CalorieCalculatorProps } from './types';

function CalculatorContent({
  showExport = true,
  initialTab = 'calculator'
}: {
  showExport: boolean;
  initialTab: TabType;
}) {
  const calculator = useCalorieCalculator();

  useEffect(() => {
    calculator.setActiveTab(initialTab);
  }, [initialTab, calculator.setActiveTab]);

  const renderActiveTab = () => {
    switch (calculator.activeTab) {
      case 'calculator':
        return <Calculator calculator={calculator} />;
      case 'results':
        return <ResultsDisplay calculator={calculator} />;
      default:
        return <Calculator calculator={calculator} />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Navigation */}
      <TabNavigation 
        activeTab={calculator.activeTab}
        onTabChange={calculator.setActiveTab}
        showResults={calculator.isCalculated}
      />

      {/* Content */}
      <main className="min-h-96">
        {renderActiveTab()}
      </main>

      {/* Export */}
      {showExport && calculator.isCalculated && (
        <div className="text-center">
          <ExportButton calculator={calculator} />
        </div>
      )}

      {/* Footer sécurité */}
      <div className="text-center bg-gradient-to-r from-neutral-50 to-neutral-100 py-6 rounded-xl border border-neutral-200">
        <p className="font-semibold text-neutral-700 mb-2">
          🔒 <strong>100% gratuit et privé</strong> • Calculs en local dans votre navigateur
        </p>
        <p className="text-xs text-neutral-500">
          Aucune donnée transmise sur nos serveurs • Export PDF inclus
        </p>
      </div>
    </div>
  );
}

export function CalorieCalculator({
  className = '',
  initialTab = 'calculator',
  showExport = true
}: CalorieCalculatorProps) {
  return (
    <div className={className}>
      <Suspense fallback={
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-16 bg-neutral-200 rounded-xl"></div>
            <div className="h-96 bg-neutral-200 rounded-xl"></div>
          </div>
        </div>
      }>
        <CalculatorContent 
          showExport={showExport}
          initialTab={initialTab}
        />
      </Suspense>
    </div>
  );
}