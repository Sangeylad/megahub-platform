// src/components/tools/beroas-calculator/BeroasCalculator.tsx
'use client';

import { Suspense, useEffect } from 'react';
import { useBeroasCalculator } from './hooks/useBeroasCalculator';
import { TabNavigation } from './components/shared/TabNavigation';
import { BasicCalculator } from './components/BasicCalculator';
import { AdvancedCalculator } from './components/AdvancedCalculator';
import { VolumeSimulator } from './components/VolumeSimulator';
import { MatrixInteractive } from './components/MatrixInteractive';
import { ExportButton } from './components/shared/ExportButton';
import type { TabType, BeroasCalculatorProps } from './types';

function CalculatorContent({ 
  showExport = true, 
  variant = 'full',
  initialTab = 'basic'
}: { 
  showExport: boolean; 
  variant: string;
  initialTab: TabType;
}) {
  const calculator = useBeroasCalculator();
  
  // ✅ Définir l'onglet initial avec les bonnes dépendances
  useEffect(() => {
    if (initialTab) {
      calculator.setActiveTab(initialTab);
    }
  }, [initialTab, calculator.setActiveTab]); // ✅ Maintenant calculator.setActiveTab est stable

  const renderActiveTab = () => {
    switch (calculator.activeTab) {
      case 'basic':
        return <BasicCalculator calculator={calculator} />;
      case 'advanced':
        return <AdvancedCalculator calculator={calculator} />;
      case 'volume':
        return <VolumeSimulator calculator={calculator} />;
      case 'matrix':
        return <MatrixInteractive calculator={calculator} />;
      default:
        return <BasicCalculator calculator={calculator} />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header - affiché seulement en mode full */}
      {variant === 'full' && (
        <div className="text-center bg-gradient-brand text-white py-12 px-8 rounded-2xl shadow-2xl">
          <h1 className="text-4xl font-bold mb-4">🎯 Calculateur BEROAS E-commerce</h1>
          <p className="text-xl opacity-95 mb-6 max-w-3xl mx-auto leading-relaxed">
            Calculez le <strong>seuil de rentabilité</strong> de vos campagnes publicitaires. 
            <strong className="block mt-2">BEROAS = Break-Even Return On Ad Spend</strong>
          </p>
          
          <div className="grid md:grid-cols-2 gap-6 mt-8 max-w-4xl mx-auto">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <div className="flex items-start gap-4">
                <span className="text-3xl">📊</span>
                <div className="text-left">
                  <div className="font-bold text-lg mb-2">ROAS</div>
                  <div className="text-sm opacity-90">
                    Chiffre d&apos;affaires généré par €1 de pub<br/>
                    <em>Si vous dépensez 100€ et générez 300€ → ROAS = 3</em>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <div className="flex items-start gap-4">
                <span className="text-3xl">🎯</span>
                <div className="text-left">
                  <div className="font-bold text-lg mb-2">BEROAS</div>
                  <div className="text-sm opacity-90">
                    ROAS minimum pour être rentable<br/>
                    <em>Si BEROAS = 2, vos campagnes doivent avoir ROAS ≥ 2</em>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation - cachée en mode minimal */}
      {variant !== 'minimal' && (
        <TabNavigation 
          activeTab={calculator.activeTab} 
          onTabChange={calculator.setActiveTab} 
        />
      )}

      {/* Content */}
      <main className="min-h-96">
        {renderActiveTab()}
      </main>

      {/* Export - conditionnel */}
      {showExport && (
        <div className="text-center">
          <ExportButton calculator={calculator} />
        </div>
      )}

      {/* Footer - affiché seulement en mode full */}
      {variant === 'full' && (
        <div className="text-center bg-gradient-to-r from-neutral-50 to-neutral-100 py-8 rounded-xl border border-neutral-200">
          <p className="font-semibold text-neutral-700 mb-2">
            🔒 <strong>100% gratuit et sécurisé</strong> • Calculs en temps réel dans votre navigateur
          </p>
          <p className="text-sm text-neutral-500">
            Aucune donnée n&apos;est envoyée sur nos serveurs - Confidentialité garantie
          </p>
        </div>
      )}
    </div>
  );
}

export function BeroasCalculator({ 
  className = '', 
  initialTab = 'basic',
  showExport = true
}: BeroasCalculatorProps) {
  return (
    <div className={className}>
      <Suspense fallback={
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-64 bg-neutral-200 rounded-2xl"></div>
            <div className="h-16 bg-neutral-200 rounded-xl"></div>
            <div className="h-96 bg-neutral-200 rounded-xl"></div>
          </div>
        </div>
      }>
        <CalculatorContent 
          showExport={showExport} 
          variant="embedded"
          initialTab={initialTab}
        />
      </Suspense>
    </div>
  );
}