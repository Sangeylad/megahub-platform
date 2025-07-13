// src/components/tools/beroas-calculator/components/MatrixInteractive.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import { InputField } from './shared/InputField';
import { MetricCard } from './shared/MetricCard';
import { formatCurrency, getBeroasCellClass } from '../utils/formatters';
import type { useBeroasCalculator } from '../hooks/useBeroasCalculator';
import type { MatrixCell } from '../types';

interface MatrixInteractiveProps {
  calculator: ReturnType<typeof useBeroasCalculator>;
}

export function MatrixInteractive({ calculator }: MatrixInteractiveProps) {
  const { generateMatrix } = calculator;
  const [matrixConfig, setMatrixConfig] = useState({
    targetBeroas: 3.0,
    paymentFees: 2.9,
    otherCosts: 2.0,
    priceMin: 15,
    priceMax: 45,
    costMin: 8,
    costMax: 20
  });
  
  const [matrixData, setMatrixData] = useState<MatrixCell[]>([]);
  const [selectedCell, setSelectedCell] = useState<MatrixCell | null>(null);
  const [showDetail, setShowDetail] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Génération de la matrice avec debounce
  const generateMatrixData = useCallback(() => {
    setIsGenerating(true);
    
    // Validation des plages
    if (matrixConfig.priceMin >= matrixConfig.priceMax || matrixConfig.costMin >= matrixConfig.costMax) {
      setIsGenerating(false);
      return;
    }

    const matrix = generateMatrix(
      matrixConfig.priceMin,
      matrixConfig.priceMax,
      matrixConfig.costMin,
      matrixConfig.costMax
    );
    
    setMatrixData(matrix);
    setIsGenerating(false);
  }, [matrixConfig, generateMatrix]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      generateMatrixData();
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [generateMatrixData]);

  const generatePriceRange = () => {
    const step = (matrixConfig.priceMax - matrixConfig.priceMin) / 11;
    return Array.from({ length: 12 }, (_, i) => matrixConfig.priceMin + (step * i));
  };

  const generateCostRange = () => {
    const step = (matrixConfig.costMax - matrixConfig.costMin) / 9;
    return Array.from({ length: 10 }, (_, i) => matrixConfig.costMin + (step * i));
  };

  const getMatrixStats = () => {
    const total = matrixData.length;
    const profitable = matrixData.filter(cell => cell.isRentable).length;
    const rate = total > 0 ? Math.round((profitable / total) * 100) : 0;
    const bestBeroas = matrixData
      .filter(cell => cell.isRentable && cell.beroas > 0)
      .sort((a, b) => a.beroas - b.beroas)[0];

    return { total, profitable, rate, bestBeroas };
  };

  const getTopCombinations = () => {
    return matrixData
      .filter(cell => cell.isRentable)
      .sort((a, b) => a.beroas - b.beroas)
      .slice(0, 3);
  };

  const generateInsights = () => {
    const stats = getMatrixStats();
    const insights = [];

    if (stats.rate === 0) {
      insights.push({
        type: 'error',
        text: `🎯 Objectif BEROAS trop strict (${matrixConfig.targetBeroas}) : aucune combinaison n&apos;est rentable. Augmentez votre objectif ou réduisez vos coûts.`
      });
    } else if (stats.rate < 20) {
      insights.push({
        type: 'warning',
        text: `⚠️ Flexibilité limitée : seulement ${stats.rate}% des combinaisons sont rentables. Votre modèle nécessite une gestion très précise.`
      });
    } else if (stats.rate > 70) {
      insights.push({
        type: 'success',
        text: `🚀 Excellente flexibilité ! ${stats.rate}% des combinaisons sont rentables. Vous avez beaucoup de marge de manœuvre.`
      });
    } else {
      insights.push({
        type: 'info',
        text: `👍 Bonne flexibilité : ${stats.rate}% des combinaisons sont rentables. Un équilibre correct entre rentabilité et contraintes.`
      });
    }

    if (matrixConfig.paymentFees > 3.5) {
      insights.push({
        type: 'warning',
        text: `💳 Frais bancaires élevés (${matrixConfig.paymentFees}%) : négociez avec votre processeur ou changez de solution pour gagner en rentabilité.`
      });
    }

    return insights;
  };

  const handleCellClick = (price: number, cost: number) => {
    const cell = matrixData.find(c => 
      Math.abs(c.price - price) < 0.1 && Math.abs(c.cost - cost) < 0.1
    );
    
    if (cell) {
      setSelectedCell(cell);
      setShowDetail(true);
    }
  };

  const applySelectedValues = () => {
    if (selectedCell) {
      calculator.updateMultipleFields({
        sellingPrice: selectedCell.price,
        productCost: selectedCell.cost
      });
      setShowDetail(false);
      
      // Switch to basic tab
      setTimeout(() => {
        calculator.setActiveTab('basic');
      }, 500);
    }
  };

  const priceRange = generatePriceRange();
  const costRange = generateCostRange();
  const stats = getMatrixStats();
  const topCombinations = getTopCombinations();
  const insights = generateInsights();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-2xl shadow-xl border border-neutral-200 overflow-hidden">
        <div className="bg-gradient-to-r from-neutral-50 to-neutral-100 px-8 py-6 border-b border-neutral-200 text-center">
          <h2 className="text-2xl font-bold text-neutral-800 mb-2">🎯 Matrice BEROAS Interactive</h2>
          <p className="text-neutral-600 leading-relaxed">
            Visualisez en temps réel quelles combinaisons prix/coûts sont rentables pour votre business. 
            <strong className="text-green-600"> Vert = Rentable</strong>, <strong className="text-red-600"> Rouge = À éviter</strong>.
          </p>
        </div>

        <div className="p-8 space-y-8">
          {/* Configuration */}
          <div className="grid lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <h3 className="font-bold text-neutral-800">⚙️ Paramètres de Rentabilité</h3>
              
              <div className="space-y-4">
                <div className="bg-neutral-50 p-4 rounded-lg">
                  <label className="block text-sm font-semibold text-neutral-700 mb-2">
                    🎯 BEROAS Objectif
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min={1.5}
                      max={6}
                      step={0.1}
                      value={matrixConfig.targetBeroas}
                      onChange={(e) => setMatrixConfig(prev => ({ 
                        ...prev, 
                        targetBeroas: parseFloat(e.target.value) 
                      }))}
                      className="flex-1 h-2 bg-brand-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <span className="font-bold text-brand-600 min-w-12">
                      {matrixConfig.targetBeroas.toFixed(1)}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-500 mt-1">
                    Votre seuil de rentabilité souhaité (plus bas = plus exigeant)
                  </p>
                </div>

                <InputField
                  label="💳 Frais bancaires (%)"
                  value={matrixConfig.paymentFees}
                  onChange={(value) => setMatrixConfig(prev => ({ ...prev, paymentFees: value }))}
                  suffix="%"
                  step={0.1}
                  max={5}
                  helpText="Commission processeur de paiement (Stripe ~2.9%, PayPal ~3.4%)"
                />

                <InputField
                  label="📋 Autres coûts (€)"
                  value={matrixConfig.otherCosts}
                  onChange={(value) => setMatrixConfig(prev => ({ ...prev, otherCosts: value }))}
                  step={0.25}
                  max={10}
                  helpText="Livraison, SAV, frais généraux par commande"
                />
              </div>
            </div>

            <div className="space-y-6">
              <h3 className="font-bold text-neutral-800">📊 Plages d&apos;Analyse</h3>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <InputField
                    label="🏷️ Prix min (€)"
                    value={matrixConfig.priceMin}
                    onChange={(value) => setMatrixConfig(prev => ({ ...prev, priceMin: value }))}
                    step={0.5}
                    min={5}
                    max={200}
                  />
                  <InputField
                    label="🏷️ Prix max (€)"
                    value={matrixConfig.priceMax}
                    onChange={(value) => setMatrixConfig(prev => ({ ...prev, priceMax: value }))}
                    step={0.5}
                    min={5}
                    max={200}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <InputField
                    label="📦 Coût min (€)"
                    value={matrixConfig.costMin}
                    onChange={(value) => setMatrixConfig(prev => ({ ...prev, costMin: value }))}
                    step={0.25}
                    min={1}
                    max={100}
                  />
                  <InputField
                    label="📦 Coût max (€)"
                    value={matrixConfig.costMax}
                    onChange={(value) => setMatrixConfig(prev => ({ ...prev, costMax: value }))}
                    step={0.25}
                    min={1}
                    max={100}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Matrice et résultats */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Matrice */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-xl border border-neutral-200 overflow-hidden">
          <div className="p-6 border-b border-neutral-200">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-neutral-800">🔍 Analyse de Rentabilité</h3>
              <div className="flex items-center gap-2 text-sm">
                <span className={isGenerating ? 'text-yellow-600' : 'text-green-600'}>
                  {isGenerating ? '🔄' : '✅'}
                </span>
                <span className="text-neutral-600">
                  {isGenerating ? 'Génération...' : `${stats.profitable} combinaisons rentables sur ${stats.total}`}
                </span>
              </div>
            </div>
          </div>

          <div className="p-6">
            {isGenerating ? (
              <div className="flex items-center justify-center h-96 bg-neutral-50 rounded-lg">
                <div className="text-center">
                  <div className="animate-spin w-12 h-12 border-4 border-brand-200 border-t-brand-500 rounded-full mx-auto mb-4"></div>
                  <p className="text-neutral-600">Génération de la matrice...</p>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr>
                      <th className="bg-neutral-700 text-white p-3 text-center font-semibold sticky top-0 z-10 border border-neutral-600">
                        Prix \ Coût
                      </th>
                      {costRange.map((cost, index) => (
                        <th key={index} className="bg-neutral-700 text-white p-3 text-center font-semibold sticky top-0 z-10 border border-neutral-600 min-w-16">
                          {cost.toFixed(1)}€
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {priceRange.map((price, priceIndex) => (
                      <tr key={priceIndex}>
                        <td className="bg-neutral-100 font-bold text-neutral-800 p-3 text-center sticky left-0 z-5 border border-neutral-300">
                          {price.toFixed(1)}€
                        </td>
                        {costRange.map((cost, costIndex) => {
                          const cell = matrixData.find(c => 
                            Math.abs(c.price - price) < 0.1 && Math.abs(c.cost - cost) < 0.1
                          );
                          
                          if (!cell) return (
                            <td key={costIndex} className="p-3 text-center border border-neutral-200">
                              --
                            </td>
                          );

                          return (
                            <td
                              key={costIndex}
                              onClick={() => handleCellClick(price, cost)}
                              className={`
                                p-3 text-center border border-neutral-200 cursor-pointer font-bold
                                transition-all hover:scale-110 hover:z-10 hover:shadow-lg
                                ${getBeroasCellClass(cell.beroas, cell.margin)}
                                ${selectedCell?.price === price && selectedCell?.cost === cost ? 'ring-4 ring-brand-500 z-20' : ''}
                              `}
                            >
                              {cell.margin > 0 ? cell.beroas.toFixed(1) : '--'}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Légende */}
          <div className="p-6 border-t border-neutral-200 bg-neutral-50">
            <h4 className="font-bold text-neutral-700 mb-3">🎨 Guide de Lecture</h4>
            <div className="grid grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-200 rounded border"></div>
                <span>🚀 Excellent (≤2.0)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-100 rounded border"></div>
                <span>✅ Très bon (≤2.5)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-100 rounded border"></div>
                <span>👍 Bon (≤3.5)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-100 rounded border"></div>
                <span>⚠️ Limite (≤5.0)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-100 rounded border"></div>
                <span>❌ Difficile (BEROAS &gt; 5.0)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-neutral-100 rounded border"></div>
                <span>🚫 Impossible</span>
              </div>
            </div>
            <p className="text-xs text-neutral-500 mt-2">
              📱 <strong>Cliquez</strong> sur une cellule pour voir le détail • 
              🎯 <strong>Cherchez</strong> le maximum de cellules vertes
            </p>
          </div>
        </div>

        {/* Résultats */}
        <div className="space-y-6">
          {/* Vue d'ensemble */}
          <div className="bg-white rounded-xl shadow-lg border border-neutral-200 p-6">
            <h3 className="font-bold text-neutral-800 mb-4">📊 Vue d&apos;Ensemble</h3>
            <div className="space-y-4">
              <MetricCard
                icon="🧮"
                label="Combinaisons"
                value={stats.total.toString()}
                variant="default"
              />
              <MetricCard
                icon="✅"
                label="Rentables"
                value={stats.profitable.toString()}
                variant="success"
              />
              <MetricCard
                icon="🎯"
                label="Taux Réussite"
                value={`${stats.rate}%`}
                variant={stats.rate > 50 ? 'success' : stats.rate > 20 ? 'warning' : 'danger'}
              />
              <MetricCard
                icon="🏆"
                label="Meilleur BEROAS"
                value={stats.bestBeroas ? stats.bestBeroas.beroas.toFixed(1) : '-'}
                variant="primary"
              />
            </div>
          </div>

          {/* Top 3 */}
          <div className="bg-white rounded-xl shadow-lg border border-neutral-200 p-6">
            <h3 className="font-bold text-neutral-800 mb-4">🏆 Top 3 Combinaisons</h3>
            {topCombinations.length > 0 ? (
              <div className="space-y-3">
                {topCombinations.map((combo, index) => {
                  const medals = ['🥇', '🥈', '🥉'];
                  return (
                    <div key={index} className="flex items-center justify-between p-3 bg-neutral-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-lg">{medals[index]}</span>
                        <div>
                          <div className="font-semibold text-sm">
                            Prix {combo.price.toFixed(1)}€ • Coût {combo.cost.toFixed(1)}€
                          </div>
                          <div className="text-xs text-neutral-600">
                            Marge {formatCurrency(combo.margin)} ({((combo.margin/combo.price)*100).toFixed(1)}%)
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600">BEROAS</div>
                        <div className="text-lg font-bold">{combo.beroas.toFixed(1)}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-neutral-500">
                <div className="text-3xl mb-2">😔</div>
                <p className="text-sm">
                  <strong>Aucune combinaison rentable</strong><br/>
                  Ajustez votre objectif BEROAS ou vos plages
                </p>
              </div>
            )}
          </div>

          {/* Insights */}
          <div className="bg-white rounded-xl shadow-lg border border-neutral-200 p-6">
            <h3 className="font-bold text-neutral-800 mb-4">💡 Insights & Recommandations</h3>
            <div className="space-y-3">
              {insights.map((insight, index) => {
                const insightClasses = {
                  success: 'border-l-green-500 bg-green-50',
                  warning: 'border-l-yellow-500 bg-yellow-50',
                  error: 'border-l-red-500 bg-red-50',
                  info: 'border-l-blue-500 bg-blue-50'
                };
                
                return (
                  <div key={index} className={`
                    border-l-4 rounded-lg p-3 text-sm leading-relaxed
                    ${insightClasses[insight.type as keyof typeof insightClasses] || insightClasses.info}
                  `}>
                    {insight.text}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Modal de détail */}
      {showDetail && selectedCell && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-neutral-200 max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-neutral-200">
              <div className="flex justify-between items-center">
                <h4 className="font-bold text-neutral-800">🔍 Analyse Détaillée</h4>
                <button
                  onClick={() => setShowDetail(false)}
                  className="w-8 h-8 rounded-full bg-neutral-100 hover:bg-neutral-200 flex items-center justify-center transition-colors"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Scénario */}
              <div className="bg-neutral-50 rounded-lg p-4 space-y-3">
                <div className="flex justify-between">
                  <span className="text-neutral-600">Prix de vente :</span>
                  <span className="font-bold">{formatCurrency(selectedCell.price)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-600">Coût produit :</span>
                  <span className="font-bold">{formatCurrency(selectedCell.cost)}</span>
                </div>
                <div className="flex justify-between bg-brand-50 -mx-2 px-2 py-2 rounded">
                  <span className="font-semibold text-brand-800">BEROAS calculé :</span>
                  <span className="font-bold text-brand-900">{selectedCell.beroas.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-600">Marge unitaire :</span>
                  <span className="font-bold">{formatCurrency(selectedCell.margin)}</span>
                </div>
              </div>

              {/* Analyse */}
              <div>
                <h5 className="font-bold text-neutral-700 mb-2">💰 Analyse de Rentabilité :</h5>
                <div className="bg-white border border-neutral-200 rounded-lg p-4 text-sm leading-relaxed">
                  {selectedCell.margin > 0 && selectedCell.beroas <= matrixConfig.targetBeroas ? (
                    <div className="text-green-700">
                      ✅ <strong>Combinaison rentable et performante</strong><br/><br/>
                      • <strong>Marge :</strong> {formatCurrency(selectedCell.margin)} par vente ({((selectedCell.margin/selectedCell.price)*100).toFixed(1)}%)<br/>
                      • <strong>Budget pub max :</strong> {formatCurrency(selectedCell.margin)} par vente<br/>
                      • <strong>BEROAS :</strong> {selectedCell.beroas.toFixed(2)} ≤ objectif ({matrixConfig.targetBeroas})<br/><br/>
                      🎯 <strong>Recommandation :</strong> Cette combinaison respecte votre seuil de rentabilité. Vous pouvez investir jusqu&apos;à {formatCurrency(selectedCell.margin)} en publicité par vente réalisée.
                    </div>
                  ) : selectedCell.margin > 0 ? (
                    <div className="text-yellow-700">
                      ⚠️ <strong>Combinaison rentable mais hors objectif</strong><br/><br/>
                      • <strong>Marge :</strong> {formatCurrency(selectedCell.margin)} par vente<br/>
                      • <strong>BEROAS :</strong> {selectedCell.beroas.toFixed(2)} &gt; objectif ({matrixConfig.targetBeroas})<br/>
                      • <strong>Écart :</strong> {(selectedCell.beroas - matrixConfig.targetBeroas).toFixed(1)} points trop élevé<br/><br/>
                      🔧 <strong>Pour atteindre votre objectif :</strong><br/>
                      Réduisez les coûts ou augmentez le prix.
                    </div>
                  ) : (
                    <div className="text-red-700">
                      ❌ <strong>Combinaison non viable</strong><br/><br/>
                      • <strong>Problème :</strong> Les coûts ({formatCurrency(selectedCell.cost)} + frais) dépassent le prix de vente<br/>
                      • <strong>Perte :</strong> {formatCurrency(Math.abs(selectedCell.margin))} par vente<br/><br/>
                      🚫 <strong>Cette configuration génère une perte systématique.</strong><br/>
                      Augmentez le prix ou réduisez drastiquement les coûts.
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={applySelectedValues}
                  className="flex-1 bg-brand-500 hover:bg-brand-600 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
                >
                  ✅ Utiliser ces Valeurs
                </button>
                <button
                  onClick={() => setShowDetail(false)}
                  className="px-4 py-3 border border-neutral-300 hover:bg-neutral-50 rounded-lg transition-colors"
                >
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}