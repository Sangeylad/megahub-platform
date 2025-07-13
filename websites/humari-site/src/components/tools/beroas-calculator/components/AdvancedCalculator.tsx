// src/components/tools/beroas-calculator/components/AdvancedCalculator.tsx
'use client';

import { InputField } from './shared/InputField';
import { MetricCard } from './shared/MetricCard';
import { formatCurrency, formatPercent, getBeroasStatusText } from '../utils/formatters';
import type { useBeroasCalculator } from '../hooks/useBeroasCalculator';

interface AdvancedCalculatorProps {
  calculator: ReturnType<typeof useBeroasCalculator>;
}

export function AdvancedCalculator({ calculator }: AdvancedCalculatorProps) {
  const { state, results, updateField } = calculator;

  const generateRecommendations = () => {
    const recommendations = [];
    
    if (results.calculatedBeroas <= 2 && results.marginPercent > 30) {
      recommendations.push({
        type: 'success',
        icon: '🚀',
        text: `BEROAS exceptionnel (${results.calculatedBeroas.toFixed(2)}) ! Vous pouvez investir massivement en publicité avec confiance.`
      });
    } else if (results.calculatedBeroas <= 3) {
      recommendations.push({
        type: 'success',
        icon: '✅',
        text: `Excellent BEROAS (${results.calculatedBeroas.toFixed(2)}) - Configuration idéale pour la croissance publicitaire.`
      });
    } else if (results.calculatedBeroas <= 4) {
      recommendations.push({
        type: 'warning',
        icon: '👍',
        text: `BEROAS correct (${results.calculatedBeroas.toFixed(2)}) mais il y a de la marge d'amélioration.`
      });
    } else {
      recommendations.push({
        type: 'error',
        icon: '⚠️',
        text: `BEROAS élevé (${results.calculatedBeroas.toFixed(2)}) - Difficile d'être rentable en publicité.`
      });
    }

    if (results.marginPercent < 15) {
      recommendations.push({
        type: 'error',
        icon: '🔴',
        text: 'Marge critique (<15%) - Votre produit n&apos;est pas viable sans optimisations majeures.'
      });
    } else if (results.marginPercent >= 50) {
      recommendations.push({
        type: 'success',
        icon: '💎',
        text: `Marge excellente (${results.marginPercent.toFixed(1)}%) - Vous avez une grande flexibilité tarifaire.`
      });
    }

    if (state.paymentFees > 3.5) {
      recommendations.push({
        type: 'warning',
        icon: '💳',
        text: 'Frais bancaires élevés (>3.5%) - Négociez avec votre processeur ou changez de solution.'
      });
    }

    if (state.platformFees > 12) {
      recommendations.push({
        type: 'warning',
        icon: '🏪',
        text: 'Commission plateforme élevée (>12%) - Considérez vendre sur votre propre site.'
      });
    }

    if (state.returnsRate > 15) {
      recommendations.push({
        type: 'warning',
        icon: '📦',
        text: 'Taux de retour élevé (>15%) - Améliorez vos descriptions produit et photos.'
      });
    }

    return recommendations;
  };

  const calculateCostsBreakdown = () => {
    const sellingPrice = state.sellingPrice;
    const shippingTotal = state.shippingCost + state.packagingCost;
    const otherTotal = state.storageCost + state.otherCosts + results.returnsImpact;

    return [
      {
        label: 'Coût produit (COGS)',
        value: state.productCost,
        percent: (state.productCost / sellingPrice) * 100
      },
      {
        label: 'Frais livraison + emballage',
        value: shippingTotal,
        percent: (shippingTotal / sellingPrice) * 100
      },
      {
        label: 'Frais bancaires',
        value: results.paymentFeesAmount,
        percent: (results.paymentFeesAmount / sellingPrice) * 100
      },
      {
        label: 'Commission plateforme',
        value: results.platformFeesAmount,
        percent: (results.platformFeesAmount / sellingPrice) * 100
      },
      {
        label: 'Autres coûts',
        value: otherTotal,
        percent: (otherTotal / sellingPrice) * 100
      }
    ];
  };

  const recommendations = generateRecommendations();
  const costsBreakdown = calculateCostsBreakdown();

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-neutral-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-neutral-50 to-neutral-100 px-8 py-6 border-b border-neutral-200">
        <h2 className="text-2xl font-bold text-neutral-800 mb-2">🚀 Calculateur BEROAS Avancé</h2>
        <p className="text-neutral-600 leading-relaxed">
          Version complète avec tous les paramètres pour une analyse précise de votre rentabilité e-commerce.
        </p>
        
        <div className="mt-4 bg-white rounded-lg p-4 border border-neutral-200">
          <span className="text-sm text-neutral-600">
            💡 <strong>BEROAS bas = Mieux</strong> (plus facile d&apos;être rentable) • 
            <strong>BEROAS élevé = Difficile</strong> (campagnes très performantes requises)
          </span>
        </div>
      </div>

      <div className="p-8 space-y-8 max-w-5xl mx-auto">
        {/* Sections d'inputs */}
        <div className="space-y-8">
          {/* Prix et Revenus */}
          <section className="bg-neutral-50 rounded-xl p-6 border border-neutral-200">
            <h3 className="text-lg font-bold text-neutral-800 mb-6 flex items-center gap-2">
              💰 Prix et Revenus
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              <InputField
                label="Prix de vente (HT)"
                value={state.sellingPrice}
                onChange={(value) => updateField('sellingPrice', value)}
              />
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-neutral-700">Taux de TVA</label>
                <select 
                  value={state.vatRate}
                  onChange={(e) => updateField('vatRate', parseFloat(e.target.value))}
                  className="w-full px-4 py-3 bg-white border-2 border-neutral-200 rounded-lg focus:border-brand-500 focus:ring-4 focus:ring-brand-100 transition-all duration-200 font-semibold"
                >
                  <option value={0}>0% (Hors TVA)</option>
                  <option value={5.5}>5,5% (Produits première nécessité)</option>
                  <option value={10}>10% (Restauration, transport)</option>
                  <option value={20}>20% (Taux normal)</option>
                </select>
              </div>
            </div>
          </section>

          {/* Coûts Directs */}
          <section className="bg-neutral-50 rounded-xl p-6 border border-neutral-200">
            <h3 className="text-lg font-bold text-neutral-800 mb-6 flex items-center gap-2">
              📦 Coûts Directs
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <InputField
                label="Coût du produit (COGS)"
                value={state.productCost}
                onChange={(value) => updateField('productCost', value)}
                helpText="Prix d'achat ou de fabrication"
              />
              <InputField
                label="Frais de livraison"
                value={state.shippingCost}
                onChange={(value) => updateField('shippingCost', value)}
                helpText="Coût de livraison par commande"
              />
              <InputField
                label="Emballage & conditionnement"
                value={state.packagingCost}
                onChange={(value) => updateField('packagingCost', value)}
                helpText="Coût emballage, étiquettes, etc."
              />
            </div>
          </section>

          {/* Frais Transactionnels */}
          <section className="bg-neutral-50 rounded-xl p-6 border border-neutral-200">
            <h3 className="text-lg font-bold text-neutral-800 mb-6 flex items-center gap-2">
              💳 Frais Transactionnels
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              <InputField
                label="Frais bancaires (% du prix HT)"
                value={state.paymentFees}
                onChange={(value) => updateField('paymentFees', value)}
                suffix="%"
                step={0.1}
                max={10}
                helpText="Stripe: ~2.9%, PayPal: ~3.4%, Banque: ~1-2%"
              />
              <InputField
                label="Commission plateforme (% du prix HT)"
                value={state.platformFees}
                onChange={(value) => updateField('platformFees', value)}
                suffix="%"
                step={0.1}
                max={20}
                helpText="Amazon: ~15%, eBay: ~10%, Shopify: 0%"
              />
            </div>
          </section>

          {/* Autres Coûts */}
          <section className="bg-neutral-50 rounded-xl p-6 border border-neutral-200">
            <h3 className="text-lg font-bold text-neutral-800 mb-6 flex items-center gap-2">
              📋 Autres Coûts
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <InputField
                label="Stockage & entreposage"
                value={state.storageCost}
                onChange={(value) => updateField('storageCost', value)}
                helpText="Coût de stockage par unité vendue"
              />
              <InputField
                label="Taux de retour (%)"
                value={state.returnsRate}
                onChange={(value) => updateField('returnsRate', value)}
                suffix="%"
                step={0.1}
                max={50}
                helpText="Moyenne e-commerce: 5-15%"
              />
              <InputField
                label="Autres coûts fixes"
                value={state.otherCosts}
                onChange={(value) => updateField('otherCosts', value)}
                helpText="SAV, marketing, frais généraux..."
              />
            </div>
          </section>

          {/* Objectifs */}
          <section className="bg-neutral-50 rounded-xl p-6 border border-neutral-200">
            <h3 className="text-lg font-bold text-neutral-800 mb-6 flex items-center gap-2">
              🎯 Objectifs
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              <InputField
                label="BEROAS cible"
                value={state.targetBeroas}
                onChange={(value) => updateField('targetBeroas', value)}
                suffix="x"
                step={0.1}
                min={1}
                helpText="Conservateur: 2-3x, Agressif: 1.5-2x"
              />
              <InputField
                label="Marge cible (%)"
                value={state.targetMargin}
                onChange={(value) => updateField('targetMargin', value)}
                suffix="%"
                step={1}
                max={80}
                helpText="Minimum viable: 20%, Idéal: 40%+"
              />
            </div>
          </section>
        </div>

        {/* Résultats détaillés */}
        <div className="space-y-8">
          <h3 className="text-xl font-bold text-neutral-800">📊 Analyse Complète</h3>
          
          {/* Métriques principales */}
          <div className="grid md:grid-cols-2 gap-6">
            <MetricCard
              icon="🎯"
              label="BEROAS Calculé"
              value={results.calculatedBeroas.toFixed(2)}
              status={getBeroasStatusText(results.calculatedBeroas, results.unitMargin)}
              variant="success"
              className="col-span-1"
            />
            
            <MetricCard
              icon="💰"
              label="Marge Unitaire"
              value={formatCurrency(results.unitMargin)}
              subtitle={formatPercent(results.marginPercent)}
              variant="primary"
              className="col-span-1"
            />
          </div>

          {/* Métriques secondaires */}
          <div className="grid md:grid-cols-4 gap-4">
            <MetricCard
              icon="💸"
              label="Budget Pub Max"
              value={formatCurrency(Math.max(0, results.unitMargin))}
            />
            <MetricCard
              icon="🏷️"
              label="Prix TTC"
              value={formatCurrency(results.sellingPriceTTC)}
            />
            <MetricCard
              icon="📉"
              label="Coûts Totaux"
              value={formatCurrency(results.totalCosts)}
            />
            <MetricCard
              icon="⚖️"
              label="Point Mort ROAS"
              value={results.calculatedBeroas.toFixed(2)}
            />
          </div>

          {/* Breakdown des coûts */}
          <div className="bg-white border border-neutral-200 rounded-xl p-6">
            <h4 className="font-bold text-neutral-800 mb-4">🔍 Détail des Coûts</h4>
            <div className="space-y-3">
              {costsBreakdown.map((cost, index) => (
                <div key={index} className="flex justify-between items-center py-3 border-b border-neutral-100 last:border-b-0">
                  <span className="text-neutral-700">{cost.label}</span>
                  <div className="text-right">
                    <span className="font-bold text-neutral-900">{formatCurrency(cost.value)}</span>
                    <span className="ml-2 text-sm bg-neutral-100 px-2 py-1 rounded text-neutral-600">
                      {cost.percent.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
              <div className="flex justify-between items-center py-3 bg-neutral-50 px-4 rounded-lg font-bold">
                <span className="text-neutral-900">Total des coûts</span>
                <div className="text-right">
                  <span className="text-neutral-900">{formatCurrency(results.totalCosts)}</span>
                  <span className="ml-2 text-sm bg-neutral-200 px-2 py-1 rounded text-neutral-700">
                    {((results.totalCosts / state.sellingPrice) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommandations */}
          <div className="bg-white border border-neutral-200 rounded-xl p-6">
            <h4 className="font-bold text-neutral-800 mb-4">💡 Recommandations Personnalisées</h4>
            <div className="space-y-3">
              {recommendations.map((rec, index) => {
                const variantClasses = {
                  success: 'bg-green-50 border-green-200 border-l-green-500',
                  warning: 'bg-yellow-50 border-yellow-200 border-l-yellow-500',
                  error: 'bg-red-50 border-red-200 border-l-red-500'
                };
                
                return (
                  <div key={index} className={`
                    border border-l-4 rounded-lg p-4 flex items-start gap-3
                    ${variantClasses[rec.type as keyof typeof variantClasses] || 'bg-neutral-50 border-neutral-200 border-l-neutral-500'}
                  `}>
                    <span className="text-lg flex-shrink-0">{rec.icon}</span>
                    <span className="text-neutral-700 leading-relaxed">{rec.text}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}