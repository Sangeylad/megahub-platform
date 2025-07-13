// src/components/tools/beroas-calculator/components/VolumeSimulator.tsx
'use client';

import { InputField } from './shared/InputField';
import { MetricCard } from './shared/MetricCard';
import { formatCurrency, formatNumber } from '../utils/formatters';
import { BeroasCalculator } from '../utils/calculations';
import type { useBeroasCalculator } from '../hooks/useBeroasCalculator';

interface VolumeSimulatorProps {
  calculator: ReturnType<typeof useBeroasCalculator>;
}

export function VolumeSimulator({ calculator }: VolumeSimulatorProps) {
  const { state, results, volumeProjections, extendedProjections, updateField } = calculator;

  const scenarios = BeroasCalculator.generateScenarios(state, results);
  const { insights, actions } = BeroasCalculator.generateROIInsights(state, volumeProjections);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-2xl shadow-xl border border-neutral-200 overflow-hidden">
        <div className="bg-gradient-to-r from-neutral-50 to-neutral-100 px-8 py-6 border-b border-neutral-200">
          <h2 className="text-2xl font-bold text-neutral-800 mb-2">📈 Simulateur de Volume & Rentabilité</h2>
          <p className="text-neutral-600 leading-relaxed">
            Projetez vos revenus, bénéfices et budgets publicitaires selon différents scénarios de croissance.
          </p>
          
          {/* Valeurs synchronisées */}
          <div className="mt-6 bg-white rounded-lg p-4 border border-neutral-200">
            <h3 className="font-semibold text-neutral-700 mb-3">⚙️ Valeurs Actuelles (synchronisées)</h3>
            <div className="grid md:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-sm text-neutral-500 mb-1">Prix de vente HT</div>
                <div className="font-bold text-neutral-800">{formatCurrency(results.sellingPriceHT)}</div>
              </div>
              <div>
                <div className="text-sm text-neutral-500 mb-1">Marge unitaire</div>
                <div className="font-bold text-neutral-800">{formatCurrency(results.unitMargin)}</div>
              </div>
              <div>
                <div className="text-sm text-neutral-500 mb-1">BEROAS</div>
                <div className="font-bold text-neutral-800">{results.calculatedBeroas.toFixed(2)}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-8 grid lg:grid-cols-3 gap-8">
          {/* Configuration */}
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-neutral-800">🎯 Paramètres de Simulation</h3>
            
            <div className="space-y-6">
              <div className="bg-brand-50 border border-brand-200 rounded-lg p-4">
                <InputField
                  label="🛒 Objectif commandes mensuelles"
                  value={state.monthlyOrders}
                  onChange={(value) => updateField('monthlyOrders', value)}
                  suffix="cmd"
                  step={10}
                  className="mb-4"
                />
                <input
                  type="range"
                  min={10}
                  max={500}
                  step={10}
                  value={state.monthlyOrders}
                  onChange={(e) => updateField('monthlyOrders', parseInt(e.target.value))}
                  className="w-full h-2 bg-brand-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-neutral-500 mt-2">
                  <span>10</span>
                  <span>250</span>
                  <span>500</span>
                </div>
              </div>
              
              <InputField
                label="📊 Taux de conversion de votre site"
                value={state.conversionRate}
                onChange={(value) => updateField('conversionRate', value)}
                suffix="%"
                step={0.1}
                min={0.1}
                max={15}
                helpText="% de visiteurs qui achètent (moyenne e-commerce : 1-3%)"
              />
              
              <InputField
                label="💸 Coût d'acquisition trafic (CPC)"
                value={state.trafficCost}
                onChange={(value) => updateField('trafficCost', value)}
                step={0.05}
                min={0.10}
                max={5.00}
                helpText="Coût moyen par clic selon votre canal publicitaire"
              />
              
              <InputField
                label="📈 Croissance mensuelle visée"
                value={state.growthRate}
                onChange={(value) => updateField('growthRate', value)}
                suffix="%"
                step={1}
                max={50}
                helpText="Croissance du nombre de commandes mois après mois"
              />
            </div>
          </div>

          {/* Projections principales */}
          <div className="lg:col-span-2 space-y-6">
            <h3 className="text-lg font-bold text-neutral-800">📊 Projections Mensuelles</h3>
            
            <div className="grid md:grid-cols-2 gap-4">
              <MetricCard
                icon="💰"
                label="Chiffre d'Affaires"
                value={formatCurrency(volumeProjections.monthlyRevenue)}
                subtitle="par mois"
                variant="primary"
              />
              
              <MetricCard
                icon="👥"
                label="Trafic Nécessaire"
                value={formatNumber(volumeProjections.requiredTraffic)}
                subtitle="visiteurs/mois"
              />
              
              <MetricCard
                icon="💸"
                label="Budget Pub Recommandé"
                value={formatCurrency(volumeProjections.recommendedBudget)}
                subtitle="pour rester rentable"
                variant="warning"
              />
              
              <MetricCard
                icon="📈"
                label="Profit Net Estimé"
                value={formatCurrency(volumeProjections.netProfit)}
                subtitle="après pub"
                variant={volumeProjections.netProfit > 0 ? 'success' : 'danger'}
              />
            </div>

            {/* Explication budget */}
            <div className="bg-brand-50 border-l-4 border-brand-500 rounded-lg p-4">
              <h4 className="font-bold text-brand-800 mb-2">💡 À propos du &ldquo;Budget Pub Recommandé&rdquo;</h4>
              <div className="text-sm text-brand-700 space-y-2">
                <p><strong>Ce budget correspond à votre seuil de rentabilité :</strong></p>
                <ul className="space-y-1 ml-4">
                  <li>✅ <strong>En dessous</strong> : Vous êtes bénéficiaire</li>
                  <li>⚖️ <strong>À ce niveau</strong> : Vous êtes à l&apos;équilibre (break-even)</li>
                  <li>❌ <strong>Au-dessus</strong> : Vous perdez de l&apos;argent</li>
                </ul>
                <p className="bg-white p-2 rounded text-brand-600">
                  <strong>Calcul :</strong> Marge unitaire × Nombre de commandes = Budget max rentable
                </p>
              </div>
            </div>

            {/* Projections étendues */}
            <div className="bg-white border border-neutral-200 rounded-xl p-6">
              <h4 className="font-bold text-neutral-800 mb-4">📅 Projections Étendues</h4>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-neutral-50 rounded-lg p-4">
                  <h5 className="font-bold text-neutral-700 mb-3 text-center">Trimestre 1</h5>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-neutral-600">CA</span>
                      <span className="font-bold">{formatCurrency(extendedProjections.q1.revenue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Commandes</span>
                      <span className="font-bold">{formatNumber(extendedProjections.q1.orders)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Profit</span>
                      <span className="font-bold">{formatCurrency(extendedProjections.q1.profit)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-neutral-50 rounded-lg p-4">
                  <h5 className="font-bold text-neutral-700 mb-3 text-center">Année 1 (avec croissance)</h5>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-neutral-600">CA</span>
                      <span className="font-bold">{formatCurrency(extendedProjections.yearly.revenue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Commandes</span>
                      <span className="font-bold">{formatNumber(extendedProjections.yearly.orders)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Profit</span>
                      <span className="font-bold">{formatCurrency(extendedProjections.yearly.profit)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scénarios dynamiques */}
      <div className="bg-white rounded-2xl shadow-xl border border-neutral-200 p-8">
        <h3 className="text-xl font-bold text-neutral-800 mb-2">🎯 Scénarios de Croissance Dynamiques</h3>
        <p className="text-neutral-600 mb-6">
          Basés sur vos paramètres (marge de {formatCurrency(results.unitMargin)}, 
          conversion {state.conversionRate}%, CPC {formatCurrency(state.trafficCost)})
        </p>
        
        <div className="grid md:grid-cols-3 gap-6">
          {scenarios.map((scenario) => {
            const variantClasses = {
              conservative: 'border-blue-200 bg-blue-50',
              current: 'border-brand-200 bg-brand-50',
              aggressive: 'border-green-200 bg-green-50'
            };
            
            return (
              <div key={scenario.id} className={`
                rounded-xl border-2 p-6 transition-all hover:shadow-lg hover:-translate-y-1
                ${variantClasses[scenario.id as keyof typeof variantClasses]}
              `}>
                <div className="flex justify-between items-center mb-4">
                  <h4 className="font-bold text-neutral-800 flex items-center gap-2">
                    {scenario.emoji} Croissance {scenario.name}
                  </h4>
                  <span className="text-xs bg-neutral-600 text-white px-2 py-1 rounded-full">
                    {scenario.badge}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-600">Commandes/mois:</span>
                    <span className="font-semibold">{formatNumber(scenario.orders)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-600">CA mensuel:</span>
                    <span className="font-semibold">{formatCurrency(scenario.revenue)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-600">Budget pub max:</span>
                    <span className="font-semibold">{formatCurrency(scenario.budget)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-600">Trafic requis:</span>
                    <span className="font-semibold">{formatNumber(scenario.traffic)}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-neutral-200">
                    <span className="font-semibold text-neutral-700">Profit potentiel:</span>
                    <span className={`font-bold ${scenario.profit > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(scenario.profit)}
                    </span>
                  </div>
                </div>
                
                <div className="mt-4 text-xs bg-white/70 p-2 rounded text-neutral-600 italic">
                  <strong>💡 Stratégie :</strong>{' '}
                  {scenario.id === 'conservative' && 'Démarrage sécurisé, focus sur l&apos;optimisation du taux de conversion'}
                  {scenario.id === 'current' && 'Équilibre croissance/risque, surveillance KPIs'}
                  {scenario.id === 'aggressive' && 'Scaling agressif, diversification des canaux d&apos;acquisition'}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Analyse & Recommandations */}
      <div className="bg-white rounded-2xl shadow-xl border border-neutral-200 p-8">
        <h3 className="text-xl font-bold text-neutral-800 mb-6">💡 Analyse & Recommandations</h3>
        
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <h4 className="font-bold text-neutral-700 mb-4">📊 Insights Clés</h4>
            <div className="space-y-3">
              {insights.map((insight, insightIndex) => (
                <div key={insightIndex} className="flex items-start gap-3 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
                  <span className="text-lg flex-shrink-0">{insight.icon}</span>
                  <span className="text-neutral-700 text-sm leading-relaxed">{insight.text}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-bold text-neutral-700 mb-4">🎯 Plan d&apos;Action</h4>
            <div className="space-y-3">
              {actions.map((action, actionIndex) => {
                const actionClasses = {
                  success: 'border-l-green-500 bg-green-50',
                  warning: 'border-l-yellow-500 bg-yellow-50',
                  error: 'border-l-red-500 bg-red-50',
                  info: 'border-l-blue-500 bg-blue-50'
                };
                
                return (
                  <div key={actionIndex} className={`
                    border-l-4 rounded-lg p-3 text-sm leading-relaxed
                    ${actionClasses[action.type as keyof typeof actionClasses] || actionClasses.info}
                  `}>
                    {action.text}
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