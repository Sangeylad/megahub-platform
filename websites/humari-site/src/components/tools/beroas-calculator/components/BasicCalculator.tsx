// src/components/tools/beroas-calculator/components/BasicCalculator.tsx
'use client';

import { useState } from 'react';
import { InputField } from './shared/InputField';
import { MetricCard } from './shared/MetricCard';
import { formatCurrency, formatPercent, getBeroasStatusText } from '../utils/formatters';
import type { useBeroasCalculator } from '../hooks/useBeroasCalculator';
import type { BenchmarkData } from '../types';

interface BasicCalculatorProps {
  calculator: ReturnType<typeof useBeroasCalculator>;
}

export function BasicCalculator({ calculator }: BasicCalculatorProps) {
  const { state, results, updateField } = calculator;
  const [showAdvancedCosts, setShowAdvancedCosts] = useState(false);
  const [showExample, setShowExample] = useState(false);
  const [showBenchmarks, setShowBenchmarks] = useState(false);

  const benchmarkData: BenchmarkData[] = [
    { sector: 'Dropshipping', range: '2.0 - 3.5', description: 'Marges serrées, concurrence forte' },
    { sector: 'Fait-main', range: '1.5 - 2.5', description: 'Marges élevées, valeur perçue forte' },
    { sector: 'Produits digitaux', range: '1.2 - 2.0', description: 'Coûts marginaux très faibles' },
    { sector: 'Mode/Beauté', range: '2.5 - 4.0', description: 'Retours fréquents, coûts logistiques' },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-neutral-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-neutral-50 to-neutral-100 px-8 py-6 border-b border-neutral-200">
        <h2 className="text-2xl font-bold text-neutral-800 mb-2">💰 Calculateur de Seuil de Rentabilité</h2>
        <p className="text-neutral-600 leading-relaxed">
          Découvrez quel ROAS minimum vos campagnes publicitaires doivent atteindre pour être rentables.
        </p>
        
        {/* Exemple pédagogique */}
        <div className="mt-6 bg-white rounded-lg border border-neutral-200 overflow-hidden">
          <button
            onClick={() => setShowExample(!showExample)}
            className="w-full px-6 py-4 text-left font-semibold text-neutral-700 hover:bg-neutral-50 transition-colors flex justify-between items-center"
          >
            📚 Voir un exemple concret
            <span className={`transform transition-transform duration-300 ${showExample ? 'rotate-45' : ''}`}>
              +
            </span>
          </button>
          
          {showExample && (
            <div className="px-6 pb-6 space-y-4 animate-in slide-in-from-top duration-200">
              <div className="space-y-3">
                <div className="flex items-center gap-4 bg-neutral-50 p-4 rounded-lg">
                  <span className="bg-brand-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">1</span>
                  <span className="text-neutral-700">Vous vendez un produit <strong>30€</strong></span>
                </div>
                <div className="flex items-center gap-4 bg-neutral-50 p-4 rounded-lg">
                  <span className="bg-brand-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">2</span>
                  <span className="text-neutral-700">Vos coûts totaux sont <strong>18€</strong> (produit + livraison + frais)</span>
                </div>
                <div className="flex items-center gap-4 bg-neutral-50 p-4 rounded-lg">
                  <span className="bg-brand-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">3</span>
                  <span className="text-neutral-700">BEROAS = 30 ÷ (30-18) = <strong>2.5</strong></span>
                </div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <strong className="text-green-800">💡 Conclusion :</strong>{' '}
                <span className="text-green-700">
                  Vos campagnes doivent avoir un ROAS ≥ {results.calculatedBeroas.toFixed(1)} pour être rentables
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="p-8 space-y-8">
        {/* Inputs principaux */}
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="relative">
              <div className="absolute -left-2 top-0 bottom-0 w-1 bg-brand-500 rounded-full"></div>
              <InputField
                label="💰 Prix de vente (HT)"
                value={state.sellingPrice}
                onChange={(value) => updateField('sellingPrice', value)}
                helpText="Prix auquel vous vendez votre produit"
                required
              />
            </div>
            
            <div className="relative">
              <div className="absolute -left-2 top-0 bottom-0 w-1 bg-brand-500 rounded-full"></div>
              <InputField
                label="📦 Coût du produit"
                value={state.productCost}
                onChange={(value) => updateField('productCost', value)}
                helpText="Prix d'achat ou de fabrication du produit"
                required
              />
            </div>
          </div>

          {/* Coûts optionnels */}
          <div className="pt-6 border-t border-neutral-100">
            <button
              onClick={() => setShowAdvancedCosts(!showAdvancedCosts)}
              className="w-full bg-neutral-50 hover:bg-neutral-100 border border-neutral-200 rounded-lg px-6 py-4 text-left font-semibold text-neutral-700 transition-colors"
            >
              ⚙️ Ajouter des coûts supplémentaires (optionnel)
            </button>
            
            {showAdvancedCosts && (
              <div className="mt-4 p-6 bg-neutral-50 rounded-lg border border-neutral-200 space-y-4 animate-in slide-in-from-top duration-200">
                <div className="grid md:grid-cols-2 gap-4">
                  <InputField
                    label="🚚 Frais de livraison"
                    value={state.shippingCost}
                    onChange={(value) => updateField('shippingCost', value)}
                  />
                  <InputField
                    label="💳 Frais bancaires"
                    value={state.paymentFees}
                    onChange={(value) => updateField('paymentFees', value)}
                    suffix="%"
                    step={0.1}
                    max={10}
                  />
                </div>
                <InputField
                  label="📋 Autres coûts fixes"
                  value={state.otherCosts}
                  onChange={(value) => updateField('otherCosts', value)}
                  helpText="SAV, frais généraux, retours..."
                />
              </div>
            )}
          </div>
        </div>

        {/* Résultats */}
        <div className="space-y-6">
          <h3 className="text-xl font-bold text-neutral-800">📊 Vos Résultats</h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              icon="💰"
              label="Marge par Vente"
              value={formatCurrency(results.unitMargin)}
              subtitle={formatPercent(results.marginPercent)}
              variant="primary"
            />
            
            <MetricCard
              icon="🎯"
              label="BEROAS (Seuil)"
              value={results.calculatedBeroas.toFixed(2)}
              status={getBeroasStatusText(results.calculatedBeroas, results.unitMargin)}
              variant="success"
            />
            
            <MetricCard
              icon="💸"
              label="Budget Pub Max"
              value={formatCurrency(Math.max(0, results.unitMargin))}
              subtitle="Par vente réalisée"
            />
            
            <MetricCard
              icon="🏷️"
              label="Prix Client Final"
              value={formatCurrency(results.sellingPriceTTC)}
              subtitle="TVA 20% incluse"
            />
          </div>

          {/* Explication BEROAS */}
          <div className="bg-white border border-neutral-200 rounded-xl p-6">
            <h4 className="font-bold text-neutral-800 mb-4">🎯 Comment utiliser votre BEROAS ?</h4>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-2xl">✅</div>
                <div>
                  <div className="font-semibold text-green-800">ROAS ≥ BEROAS</div>
                  <div className="text-sm text-green-600">Vos campagnes sont rentables</div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-2xl">❌</div>
                <div>
                  <div className="font-semibold text-red-800">ROAS &lt; BEROAS</div>
                  <div className="text-sm text-red-600">Vous perdez de l&apos;argent</div>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="text-2xl">⚖️</div>
                <div>
                  <div className="font-semibold text-yellow-800">ROAS = BEROAS</div>
                  <div className="text-sm text-yellow-600">Vous êtes à l&apos;équilibre</div>
                </div>
              </div>
            </div>
          </div>

          {/* Benchmarks sectoriels */}
          <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowBenchmarks(!showBenchmarks)}
              className="w-full px-6 py-4 text-left font-semibold text-neutral-700 hover:bg-neutral-50 transition-colors flex justify-between items-center"
            >
              📊 Voir les benchmarks BEROAS par secteur
              <span className={`transform transition-transform duration-300 ${showBenchmarks ? 'rotate-45' : ''}`}>
                +
              </span>
            </button>
            
            {showBenchmarks && (
              <div className="px-6 pb-6 space-y-4 animate-in slide-in-from-top duration-200">
                <p className="text-sm text-neutral-500 italic bg-brand-50 p-3 rounded-lg border-l-4 border-brand-500">
                  Données basées sur l&apos;analyse de 500+ e-commerces français (2023-2024) - Sources : études sectorielles & retours clients
                </p>
                <div className="grid md:grid-cols-2 gap-4">
                  {benchmarkData.map((benchmark, index) => (
                    <div key={index} className="bg-neutral-50 rounded-lg p-4 border border-neutral-200 text-center">
                      <div className="font-bold text-neutral-800 mb-2">{benchmark.sector}</div>
                      <div className="text-xl font-bold text-brand-600 mb-2">{benchmark.range}</div>
                      <div className="text-sm text-neutral-600">{benchmark.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}